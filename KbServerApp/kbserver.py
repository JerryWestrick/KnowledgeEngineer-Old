import json
import os
import time
from typing import List

from autobahn.twisted.websocket import WebSocketServerProtocol
from dotenv import load_dotenv, find_dotenv
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.logger import Logger

from KbServerApp.OpenAI_API_Costs import OpenAI_API_Costs
from KbServerApp.Processes import ProcessList, ProcessList_save, ProcessList_load
from KbServerApp.logger import GptLogger
from KbServerApp.step import Step

load_dotenv(find_dotenv())


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

        msg = {}
        # If a database connection was defined, then send the initial load
        if self.factory.db is not None:
            msg = {'cmd': 'db_initial_load',
                   'cb': 'db_initial_load',
                   'rc': 'Okay',
                   'object': 'db_initial_load',
                   'data': self.factory.db.sql_database_tables
                   }
            response = json.dumps(msg, ensure_ascii=False, default=str)
            self.sendMessage(response.encode('UTF8'), False)
        KbServerProtocol.log.info("Now Serving {count} clients", count=len(self.factory.webClients))

        # process_list_initial_load
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

        # memory_initial_load
        msg['cmd'] = 'memory_initial_load'
        msg['cb'] = 'memory_initial_load'
        msg['rc'] = 'Okay'
        msg['object'] = 'memory'
        msg['data'] = self.memory_as_dictionary()
        response = json.dumps(msg, ensure_ascii=False, default=str)
        self.sendMessage(response.encode('UTF8'), False)

        # memory_initial_load
        msg['cmd'] = 'models_initial_load'
        msg['cb'] = 'models_initial_load'
        msg['rc'] = 'Okay'
        msg['object'] = 'models'
        msg['data'] = OpenAI_API_Costs
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
                try:
                    path = os.path.join(dirpath, filename)
                    with open(path, 'r') as f:
                        content = f.read()
                        subtree[filename] = content
                except UnicodeDecodeError:
                    KbServerProtocol.log.error("Could not read file {fname}", fname=path)



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
    def schedule(self, pname: str, tasklist: List[Step]):
        # tasklist: List[Step] = ProcessList[pname]
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
            GptLogger(f'Memory/Dynamic/Logs/{process_name}.log')  # Is a singleton, so ignore result.
            tasklist: List[Step] = ProcessList[process_name]
            yield self.schedule(process_name, tasklist)
            msg['rc'] = 'Okay'
            msg['reason'] = 'Run Completed'
            msg['data'] = {'one': 'two'}
            msg['cmd'] = 'Process'
            msg['object'] = 'Test'
        elif msg['cmd'] == 'exec' and msg['object'] == 'step':
            process_name = msg['record']['process_name']
            step_name = msg['record']['step_name']
            KbServerProtocol.log.info(f"Call to run a single step {process_name}::{step_name}")
            GptLogger(f'Memory/Dynamic/Logs/{process_name}_{step_name}.log')  # Is a singleton, so ignore result.
            tasklist: List[Step] = ProcessList[process_name]
            steps = [step for step in tasklist if step.name == step_name]
            yield self.schedule(process_name,  steps)
            msg['rc'] = 'Okay'
            msg['reason'] = 'Run Completed'
            msg['data'] = {'one': 'two'}
            msg['cmd'] = 'Process'
            msg['object'] = 'Test'
        elif msg['cmd'] == 'read':
            prompt_name = msg['object']
            KbServerProtocol.log.info(f"Call to test read {prompt_name}...")
            msg['rc'] = 'Okay'
            msg['reason'] = 'Test Read Complete'
            try:
                expanded_text = Step.memory[prompt_name]
            except KeyError as key:
                expanded_text = [{'role': 'Error', 'content': f'Expansion of {prompt_name} failed.'},
                                 {'role': 'Error', 'content': f'Could not find {key} in memory.'}
                                 ]
                msg['rc'] = 'Fail'
                msg['reason'] = 'Test Read Failed'

            msg['data'] = {'text':  expanded_text}
        elif msg['cmd'] == 'write':
            prompt_name = msg['object']
            KbServerProtocol.log.info(f"Call to write {prompt_name}...")
            msg['rc'] = 'Okay'
            msg['reason'] = f'Write of {prompt_name} Complete'
            msg['data'] = msg['record']
            try:
                Step.memory[prompt_name] = msg['record']['text']
                KbServerProtocol.log.info(f"Call to write {prompt_name} complete.")
            except KeyError as key:
                msg['rc'] = 'Fail'
                msg['reason'] = f'write of {prompt_name} Failed'

        elif msg['cmd'] == 'save_step':
            process_name = msg['record']['process_name']
            new_step = msg['record']['step']
            step_name = new_step['name']
            KbServerProtocol.log.info(f"Call to write step {process_name}::{step_name}...")
            msg['rc'] = 'Okay'
            msg['reason'] = f'Write of step {process_name}::{step_name} Complete'
            msg['data'] = msg['record']
            tasklist: List[Step] = ProcessList[process_name]
            for idx, step in enumerate(tasklist):
                if step.name == step_name:
                    tasklist[idx] = Step.from_json(new_step)
                    break
            ProcessList_save(ProcessList)
            KbServerProtocol.log.info(f"Call to write step {process_name}::{step_name}...")

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
