import json
import threading
from typing import List, Callable

import psycopg
import twisted
from dotenv import load_dotenv, find_dotenv
from psycopg import Notify
from psycopg.rows import dict_row
from twisted.application.service import Service
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.logger import Logger

from KbServerApp.defered import as_deferred

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

