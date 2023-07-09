import json
import os
import threading
import time
from typing import List, Callable

import psycopg
import twisted
from autobahn.twisted.websocket import WebSocketServerProtocol
from dotenv import load_dotenv, find_dotenv
from psycopg import Notify
from psycopg.rows import dict_row
from twisted.application.service import Service
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.logger import Logger
from twisted.internet import protocol, reactor

from KbServerApp.OpenAI_API_Costs import OpenAI_API_Costs
from KbServerApp.Processes import ProcessList
from KbServerApp.defered import as_deferred
from KbServerApp.logger import GptLogger
from KbServerApp.step import Step

load_dotenv(find_dotenv())


class DatabaseStore(object):
    log = Logger(namespace='DatabaseStore')

    # database access information
    dsn = 'application_name=KnowledgeEngineer'
    sql_database_tables = {}

    # List of database Tables to be supported
    sql_tables_to_watch = ['steps', 'users']

    # The sql_table_commands dict id generated from DDL info using this SQL
    sql_select_all_columns = '''select table_schema, table_name, ordinal_position, column_name
                                from information_schema.columns
                                where table_schema = 'public' and table_name = %(table_name)s
                                order by table_name, ordinal_position;
                                '''

    sql_table_commands = {
        # 'job': {
        #     'insert': 'insert into job (title, company, location, characteristics, description) values '
        #               '(%(title)s, %(company)s, %(location)s, %(characteristics)s, %(description)s);',
        #     'update': 'update job set title = %(title)s, company = %(company)s, location = %(location)s, '
        #               'characteristics = %(characteristics)s, description = %(description)s where id = %(id)s;',
        #     'delete': 'delete from job where id = %(id)s;'
        # }
    }

    def __init__(self, factory):
        self.factory = factory
        self._load_database()

    async def _execute_sql(self, msg):
        table_name = msg['object']
        command = msg['cmd'].lower()
        sql = self.sql_table_commands[table_name][command]
        async with await psycopg.AsyncConnection.connect(self.dsn) as a_connection:
            async with a_connection.cursor() as a_cursor:
                await a_cursor.execute(sql, msg['record'])

    async def _get_new_record(self, sql):
        async with await psycopg.AsyncConnection.connect(self.dsn) as a_connection:
            async with a_connection.cursor(row_factory=dict_row) as a_cursor:
                await a_cursor.execute(sql)
                row = await a_cursor.fetchone()
        return row

    def _load_database(self):
        self.log.info("Loading Tables {tables!r}", tables=self.sql_tables_to_watch)
        with psycopg.connect(self.dsn) as conn:
            # Open a cursor to perform database operations
            with conn.cursor(row_factory=dict_row) as cur:
                for table_name in self.sql_tables_to_watch:
                    # Query the database and obtain data as Python objects.
                    cur.execute(f'SELECT * FROM "{table_name}"')
                    tab = {}
                    for row in cur.fetchall():
                        tab[row['id']] = row
                    self.sql_database_tables[table_name] = tab
                    self.log.info("Loaded {rows} rows in {table}", rows=len(tab), table=table_name)

                    # Load table description
                    cur.execute(self.sql_select_all_columns, {'table_name': table_name})
                    cols = []
                    for row in cur.fetchall():
                        if row['column_name'] != 'id':
                            cols.append(row['column_name'])
                    ins_stmt = f'insert into "{table_name}" (' + ', '.join(cols) + ') values ' + '(%(' + ')s, %('.join(
                        cols) + ')s);'
                    upd_stmt = 'update "{table_name}" set '
                    for col in cols:
                        upd_stmt += f'{col} = %({col})s, '
                    upd_stmt += 'where id = %(id)s;'

                    self.sql_table_commands[table_name] = {
                        'insert': ins_stmt,
                        'update': upd_stmt,
                        'delete': f'delete from "{table_name}" where id = %(id)s;'
                    }
            # @TODO Get the auto generated id back from insert.
            #       This needs to be returned in the response to the insert
            #       To allow the issuer to identify the record he inserted.

            # Make the changes to the database persistent
            conn.commit()
            self.log.info("All Tables Loaded")

    @inlineCallbacks
    def receive_notify(self, notify: Notify):
        self.log.info("Event: {notify!r}", notify=notify)
        (table_name_str, cmd, id_str) = notify.payload.split(',')
        table_name = table_name_str[1: -1]  # Remove the quotes
        record_id_str = id_str.split('=')[1]
        record_id = int(record_id_str[1: -1])
        records: dict = self.sql_database_tables[table_name]
        record = None
        old = records[record_id]  # save old record to send

        # Update Self sql_database_tables
        # execute change to table
        if cmd in ('I', 'U'):
            self.log.info("Event: {notify!r} About to read new record SQL", notify=notify)
            record = yield as_deferred(self._get_new_record(f'select * from {table_name} where id={record_id}'))
            records[record_id] = record

        elif cmd == 'D':
            del records[record_id]
        else:
            self.log.error("Notify Event of Unknown format {notify}", notify=notify)
            return

        # Build msg
        msg = {'cmd': cmd,
               'object': table_name,
               'cb': 'db_async_notification',
               'id': record_id,
               'record': record,
               'old': old,
               }

        self.log.info(f"DB Async Notification: {cmd} {table_name}", cmd=cmd, table_name=table_name)
        # Send message to all connected clients
        response = json.dumps(msg, ensure_ascii=False).encode('UTF8')
        for client in self.factory.webClients:
            # @TODO Client Security Implementation goes Here...
            #   Only send message if client is allowed to see it.
            client.sendMessage(response, False)
        self.log.info("DB Mod sent to all connections")

    @inlineCallbacks
    # Twisted Async Routine
    def make_change(self, msg):
        try:
            self.log.info("About to execute db change {cmd} {object} ...", **msg)
            yield as_deferred(self._execute_sql(msg))  # psycopg 3 Async Routine
        except BaseException:
            self.log.failure("{cmd} of {object} failed", **msg)

        returnValue(None)

    async def users_login(self, msg) -> int:
        sql = "update users set last_login = now() " \
              "where  email = %(email)s " \
              "and    password = crypt(%(password)s, password)"

        async with await psycopg.AsyncConnection.connect(self.dsn) as a_connection:
            async with a_connection.cursor() as a_cursor:
                await a_cursor.execute(sql, msg['record'])
                return a_cursor.rowcount


class PostgresListenService(twisted.application.service.Service):
    """
    PostgresSQL LISTEN/NOTIFY as Twisted Service

    This implementation uses psycopg3, and a separate thread.


    Usage:  in the .tac file you need:

        1- Setup separate thread to receive asynchronous event Notifications:

            notification_service = PostgresListenService(cb_object=obj, cb_routine, events)
            notification_service.setServiceParent(application)

        2- cb_object.cb_routine(Notify) will be called with each notify
    """

    log = Logger()

    def __init__(self, db: DatabaseStore):
        self.stopped: bool = True
        self.db = DatabaseStore
        self.dsn: str = db.dsn
        self.cb_routine: Callable = db.receive_notify
        self.events: List[str] = db.sql_tables_to_watch

    @inlineCallbacks
    def notify_rtn(self, notify: tuple):
        # This Routine is called from within the Twisted Thread
        # and therefore has access to full python / twisted functionality
        #
        PostgresListenService.log.info("Event: {notify!r}", notify=notify)
        try:
            yield self.cb_routine(notify)  # Process The Event...
        except Exception:
            PostgresListenService.log.failure("Error occurred in PostgresListenService Callback ")

    def run(self, events: List[str]):
        # =================================================
        # == This routine is run in a Separate Thread!!! ==
        # =================================================
        # Do NOT use twisted functions, Do Not access other objects, DO NOT...
        # *** MultiThreading is difficult, don't start messing with it ***
        #
        PostgresListenService.log.info("In thread %s connecting to DB" % (threading.get_ident()))

        with psycopg.connect(self.dsn, autocommit=True) as self.conn:

            for channel in events:
                PostgresListenService.log.info("LISTEN {channel}", channel=channel)
                self.conn.execute(f"LISTEN {channel}")

            self.conn.execute("LISTEN stop")
            PostgresListenService.log.info("Awaiting Events {events}, and stop ", events=events)

            for notify in self.conn.notifies():
                if notify.channel == 'stop':
                    PostgresListenService.log.info("In thread {tid}: Received stop command... Thread is terminating",
                                                   tid=threading.get_ident())
                    return
                # We are running in a separate thread...
                # We need to get a message into the Twisted Server Thread...
                # So we do reactor.callFromThread(rtn, params),
                # which tells Twisted to call rtn from within the twisted Thread with params
                #
                reactor.callFromThread(self.notify_rtn, notify)

    def service_stopped(self):
        PostgresListenService.log.info("Clean Shutdown")

    def startService(self):
        self.stopped = False
        # From Twisted Thread start a new thread to process postgres Notifications...
        reactor.callInThread(self.run, DatabaseStore.sql_tables_to_watch)
        Service.startService(self)

    def stopService(self):
        PostgresListenService.log.info("Got stopService()... Issuing stop event to async thread")

        # @TODO This implements an async command channel built through the database comms.
        #   The example issues a 'stop' command.  **THIS IS NOT GOOD**
        #   - This will stop all apps connected to DB and listening for 'stop' **NOT JUST THIS SERVER**
        #       some sort of Id needs to be added to identify individual services maybe 'hostname:thread_id'
        #       of course stop all services is a valid command, just not what is desired here.
        #   - This needs to be extended to implement a general async command channel that can issue
        #       commands to individual or all services running.
        #       i.e. 'Debug(logging=on)', 'refresh_cache', 'Chat("Can I help you?")', 'Advert("IBM is hiring!")', etc

        with psycopg.connect(DatabaseStore.dsn, autocommit=True) as conn:
            conn.execute("NOTIFY stop")

        self.stopped = True
        Service.stopService(self)


WS_CONNECTIONS = []  # All connection instances


class KbServerProtocol(WebSocketServerProtocol):
    #
    # This is instantiated for each connection...
    # this is the Per Connection Storage.
    #

    # Class Variables
    log = Logger(namespace='KbServerProtocol')

    # We have a valid connection...
    def __init__(self):
        super().__init__()
        self.loggedIn = False
        self.user = {}
        WS_CONNECTIONS.append(self)

    def onOpen(self):
        KbServerProtocol.log.info("onOpen()...")

        # Yippee, we got a valid Login..  Store the
        self.factory.webClients.append(self)
        self.loggedIn = True

        msg = {'cmd': 'db_initial_load',
               'cb': 'db_initial_load',
               'rc': 'Okay',
               'object': 'db_initial_load',
               'data': self.factory.db.sql_database_tables
               }
        response = json.dumps(msg, ensure_ascii=False, default=str)
        self.sendMessage(response.encode('UTF8'), False)
        KbServerProtocol.log.info("Now Serving {count} clients", count=len(self.factory.webClients))
        pl = {}
        for k, v in ProcessList.items():
            a = []
            for s in v:
                a.append(s.to_json())
            pl[k] = a

        msg['cmd'] = 'process_list_initial_load'
        msg['cb'] = 'process_list_initial_load'
        msg['rc'] = 'Okay'
        msg['object'] = 'process'
        msg['data'] = pl
        response = json.dumps(msg, ensure_ascii=False, default=str)
        self.sendMessage(response.encode('UTF8'), False)

        msg['cmd'] = 'memory_initial_load'
        msg['cb'] = 'memory_initial_load'
        msg['rc'] = 'Okay'
        msg['object'] = 'memory'
        msg['data'] = self.memory_as_dictionary()
        response = json.dumps(msg, ensure_ascii=False, default=str)
        self.sendMessage(response.encode('UTF8'), False)

        return

    def memory_as_dictionary(self):
        dir_structure = {}

        for dirpath, dirnames, filenames in os.walk('Memory'):
            subtree = dir_structure
            dirpath_parts = dirpath.split(os.sep)

            for part in dirpath_parts[1:]:
                subtree = subtree.setdefault(part, {})

            for dirname in dirnames:
                subtree.setdefault(dirname, {})

            for filename in filenames:
                path = os.path.join(dirpath, filename)
                with open(path, 'r') as f:
                    content = f.read()
                subtree[filename] = content

        return dir_structure

    def onClose(self, was_clean, code, reason):
        if self in self.factory.webClients:
            self.factory.webClients.remove(self)
        if self.user:
            KbServerProtocol.log.info("User: {user} Logged out.  Now Serving {count} clients", user=self.user['email'],
                                      count=len(self.factory.webClients))
        else:
            KbServerProtocol.log.info("Disconnect of failed channel.  Now Serving {count} clients",
                                      count=len(self.factory.webClients))
        WS_CONNECTIONS.remove(self)

    def message(self, message):
        self.transport.write(message + b"\n")

    @inlineCallbacks
    def schedule(self, pname: str):
        tasklist: List[Step] = ProcessList[pname]
        start_time = time.time()
        prompt_tokens = 0
        completion_tokens = 0
        total_tokens = 0
        p_cost = 0.0
        c_cost = 0.0
        total = 0.0

        for step in tasklist:
            ai_model = step.ai.model
            pricing = OpenAI_API_Costs[ai_model]
            yield step.run(self, pname)
            prompt_tokens += step.prompt_tokens
            completion_tokens += step.completion_tokens
            total_tokens += step.total_tokens
            sp_cost = pricing['input'] * (step.prompt_tokens / 1000)
            sc_cost = pricing['output'] * (step.completion_tokens / 1000)
            s_total = sp_cost + sc_cost
            p_cost += sp_cost
            c_cost += sc_cost
            total += p_cost + c_cost
            GptLogger.log('STEP', f'Cost Estimate: Total: {s_total:.4f} ('
                                  f' Prompt: {sp_cost:.4f}'
                                  f' Completion: {sc_cost:.4f})')

        elapsed = time.time() - start_time
        GptLogger.log('RUN', f'Elapsed: {elapsed:.2f}s'
                             f' Cost Estimate: Total: {total:.4f} ('
                             f' Prompt: {p_cost:.4f}'
                             f' Completion: {c_cost:.4f})')

        # Logger.log('RUN', f'Estimated Cost: Total: ${total:.4f}, (Prompt: ${p_cost:.4f}, Completion: ${c_cost:.4f})')

    @inlineCallbacks
    def onMessage(self, payload, isbinary):
        if not self.loggedIn:
            yield self.user_login(payload, isbinary)
            returnValue('')

        msg = json.loads(payload.decode('utf8'))
        KbServerProtocol.log.info("received msg cmd:{cmd} object:{object} ...", **msg)

        if msg['cmd'] == 'exec' and msg['object'] == 'process':
            process_name = msg['record']['process']
            KbServerProtocol.log.info(f"Call to run {process_name}.....")
            Logger(f'Memory/Dynamic/Logs/{process_name}.log')  # Is a singleton, so ignore result.
            yield self.schedule(process_name)
            msg['rc'] = 'Okay'
            msg['reason'] = 'Run Completed'
            msg['data'] = {'one': 'two'}
            msg['cmd'] = 'Process'
            msg['object'] = 'Test'
        else:
            try:
                yield self.factory.db.make_change(msg=msg)
            except Exception as err:
                KbServerProtocol.log.error("message not processed...reason({err})", err=err)
                msg['rc'] = 'Fail'
                msg['reason'] = f"message not processed...reason({err})"

        response = json.dumps(msg, ensure_ascii=False)
        self.sendMessage(response.encode('UTF8'), isbinary)
        returnValue('')


from twisted.internet import inotify
from twisted.python import filepath


def notify(ignored, fp, mask):
    """
    For historical reasons, an opaque handle is passed as first
    parameter. This object should never be used.

    @param filepath: FilePath on which the event happened.
    @param mask: inotify event as hexadecimal masks
    """
    fn = fp.asTextMode()  # encode('utf-8')# decode('utf-8')
    [path, ext] = fn.splitext()

    # Ignore backup files
    if ext != '' and ext[-1] == '~':
        return

    path_list = path.split(fn.sep)
    start_idx = path_list.index('Memory') + 1
    p = path_list[start_idx:-1]
    n = f'{path_list[-1]}{ext}'
    m = inotify.humanReadableMask(mask)

    if 'delete' in m:
        content = ''
    else:
        content = fp.getContent().decode('utf-8')

    print(f"event {', '.join(m)} on {'/'.join(p)}/{n}: {content[:80]}")
    msg = {'cmd': 'memory_update',
           'cb': 'memory_update',
           'rc': 'Okay',
           'object': 'memory',
           'data': {
               'mask': m,
               'path': p,
               'name': n,
               'content': content,
                }
           }

    response = json.dumps(msg, ensure_ascii=False)
    for conn in WS_CONNECTIONS:
        conn.sendMessage(response.encode('UTF8'), False)


notifier = inotify.INotify()
notifier.startReading()
notifier.watch(filepath.FilePath("Memory"),
               mask=inotify.IN_WATCH_MASK,
               autoAdd=True,
               callbacks=[notify],
               recursive=True,
               )
