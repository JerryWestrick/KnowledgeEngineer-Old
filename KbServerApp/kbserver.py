import copy
import json
import os
import shutil
import time
import traceback
from typing import List

import jsonpickle
from autobahn.twisted.websocket import WebSocketServerProtocol
from dotenv import load_dotenv, find_dotenv
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.logger import Logger

from KbServerApp.OpenAI_API_Costs import OpenAI_API_Costs
from KbServerApp.Processes import ProcessList, ProcessList_save, ProcessList_load
# from KbServerApp.logger import GptLogger
from KbServerApp.step import Step

load_dotenv(find_dotenv())

WS_CONNECTIONS = []  # All connection instances

empty_step_json = '''{
      "py/object": "KbServerApp.step.Step",
      "name": "New Step",
      "prompt_name": "",
      "verify_prompt": "",
      "storage_path": "",
      "text_file": "",
      "file_process_enabled": false,
      "file_process_name": "",
      "file_glob": "",
      "macros": {},
      "ai": {
        "py/object": "KbServerApp.ai.AI",
        "temperature": 0,
        "max_tokens": 3000,
        "model": "gpt-3.5-turbo",
        "messages": [],
        "answer": "",
        "files": {},
        "mode": "chat",
        "e_stats": {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "sp_cost": 0.0,
            "sc_cost": 0.0,
            "s_total": 0.0,
            "elapsed_time": 0.0
        }
      }
}
'''


# @todo Replace json.dumps with jsonpickle
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
                   'record': self.factory.db.sql_database_tables
                   }
            response = json.dumps(msg, ensure_ascii=False, default=str)
            self.sendMessage(response.encode('UTF8'), False)
        KbServerProtocol.log.info("Now Serving {count} clients", count=len(self.factory.webClients))

        self.process_list_initial_load()
        self.memory_initial_load()
        self.models_initial_load()
        return

    def process_list_initial_load(self):
        pl = {}
        for k, v in ProcessList.items():
            a = []
            for s in v:
                a.append(s.to_json())
            pl[k] = a
        msg = {'cmd': 'process_list_initial_load', 'cb': 'process_list_initial_load',
               'rc': 'Okay', 'object': 'process', 'record': pl}
        self.send_object(msg)

    def memory_initial_load(self):
        msg = {'cmd': 'memory_initial_load', 'cb': 'memory_initial_load',
               'rc': 'Okay', 'object': 'memory', 'record': self.memory_as_dictionary()}
        self.send_object(msg)

    def models_initial_load(self):
        msg = {'cmd': 'models_initial_load', 'cb': 'models_initial_load',
               'rc': 'Okay', 'object': 'models', 'record': OpenAI_API_Costs}
        self.send_object(msg)

    def memory_as_dictionary(self):
        dir_structure = {}

        # @todo: 'Memory' should be parameter and not constant!
        for dirpath, dirnames, filenames in os.walk('Memory'):
            subtree = dir_structure
            dirpath_parts = dirpath.split(os.sep)

            for part in dirpath_parts[1:]:
                subtree = subtree.setdefault(part, {})

            for dirname in dirnames:
                subtree.setdefault(dirname, {})

            for filename in filenames:
                path = os.path.join(dirpath, filename)
                try:
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
    def generate_file_process(self, process_name, step):
        # Generate a step in a process for each file in glob...
        process_to_generate = step.file_process_name
        file_glob = step.file_glob

        process = []
        KbServerProtocol.log.info(f"Call to generate_file_process {process_to_generate}...")
        files = Step.memory.glob_files(file_glob)
        for filename in sorted(files):
            step_name = filename.split('.')[0]
            step_name = step_name.split('/')[-1]
            step_copy = copy.deepcopy(step)
            step_copy.macros['pathname'] = filename
            step_copy.macros['filename'] = os.path.basename(filename)
            step_copy.macros['path'] = os.path.dirname(filename)
            step_copy.name = step_name
            step_copy.file_process_enabled = False
            process.append(step_copy)

        KbServerProtocol.log.info(f"Saving Generated {process_to_generate} with {len(files)} steps...")
        ProcessList[process_to_generate] = process
        ProcessList_save(ProcessList)
        self.process_list_initial_load()

        msg = {'cmd': 'exec',
               'cb': 'cb_exec_process',
               'rc': 'Okay',
               'object': 'process',
               'record': {'process_name': process_to_generate}
               }
        yield self.exec_process(msg, False)
        KbServerProtocol.log.info(f"Generation and Execution of {process_to_generate} from {process_name}{step.name} complete...")

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

            if step.file_process_enabled:
                yield self.generate_file_process(pname, step)
                continue

            ai_model = step.ai.model
            pricing = OpenAI_API_Costs[ai_model]
            try:
                yield step.run(self, pname)
            except Exception as err:
                tb_str = traceback.format_exc()
                err_msg = str(err)
                self.log.error("Error in step.run(): {err_msg}", err_msg=err_msg)
                raise

            prompt_tokens += step.ai.e_stats['prompt_tokens']
            completion_tokens += step.ai.e_stats['completion_tokens']
            total_tokens += step.ai.e_stats['total_tokens']
            sp_cost = pricing['input'] * (step.ai.e_stats['prompt_tokens'] / 1000)
            sc_cost = pricing['output'] * (step.ai.e_stats['completion_tokens'] / 1000)
            p_cost += sp_cost
            c_cost += sc_cost
            total += p_cost + c_cost

        elapsed = time.time() - start_time
        self.log.info(
          f'Total Run Elapsed: {elapsed:.2f}s \n {" "*50}Cost Estimate: Total: {total:.4f} ( Prompt: {p_cost:.4f} Completion: {c_cost:.4f})'
        )

    @inlineCallbacks
    def exec_step(self, msg, isbinary):
        process_name = msg['record']['process_name']
        step_name = msg['record']['step_name']
        KbServerProtocol.log.info(f"Call to run a single step {process_name}::{step_name}")
        # GptLogger(f'Memory/Dynamic/Logs/{process_name}_{step_name}.log')  # Is a singleton, so ignore result.
        tasklist: List[Step] = ProcessList[process_name]
        steps = [step for step in tasklist if step.name == step_name]
        try:
            yield self.schedule(process_name, steps)
        except:
            self.log.error(f'Error in self.schedule()')
            raise

        msg['rc'] = 'Okay'
        msg['reason'] = 'Run Completed'
        msg['record'] = {'one': 'two'}
        msg['cmd'] = 'Process'
        msg['object'] = 'Test'
        self.send_object(msg)
        returnValue('')

    @inlineCallbacks
    def exec_process(self, msg, isbinary):
        process_name = msg['record']['process_name']
        if process_name not in ProcessList:
            msg['rc'] = 'Error'
            msg['reason'] = f'Process {process_name} not found.'
            self.send_object(msg)
            returnValue('')

        KbServerProtocol.log.info(f"Call to run {process_name}.....")
        # GptLogger(f'Memory/Dynamic/Logs/{process_name}.log')  # Is a singleton, so ignore result.
        tasklist: List[Step] = ProcessList[process_name]
        try:
            yield self.schedule(process_name, tasklist)
        except:
            self.log.error(f"Error in self.schedule()")
            raise

        msg['rc'] = 'Okay'
        msg['reason'] = 'Run Completed'
        self.send_object(msg)
        returnValue('')

    def test_memory(self, msg, isbinary):
        prompt_name = msg['record']['prompt_name']
        KbServerProtocol.log.info(f"Call to test read memory {prompt_name}...")
        msg['rc'] = 'Okay'
        msg['reason'] = 'Test Read Complete'
        try:
            expanded_text = Step.memory[prompt_name]
        except KeyError as key:
            expanded_text = [{'role': 'Error', 'content': f'Expansion of {prompt_name} failed.'},
                             {'role': 'Error', 'content': f'Could not find {key} in memory.'}
                             ]
            msg['rc'] = 'Fail'
            msg['reason'] = f'Test Read Failed Key {key} not found'
            self.send_object(msg)
            return

        msg['record'] = {'text': expanded_text}
        self.send_object(msg)
        return

    def test_file_glob(self, msg, isbinary):
        filename = msg['record']['file_glob']
        KbServerProtocol.log.info(f"Call to test file Glob {filename}...")
        msg['rc'] = 'Okay'
        msg['reason'] = 'Test File Glob Complete'
        try:
            files = Step.memory.glob_files(filename)
        except KeyError as key:
            expanded_text = [{'role': 'Error', 'content': f'Expansion of {filename} failed.'},
                             ]
            msg['rc'] = 'Fail'
            msg['reason'] = f'Test File Glob Failed {filename} not found'
            self.send_object(msg)
            return
        paths = sorted(files)
        msg['record']['path'] = os.path.dirname(filename)
        msg['record']['files'] = paths
        self.send_object(msg)
        return

    def write_memory(self, msg, isbinary):
        prompt_name = msg['record']['prompt_name']
        KbServerProtocol.log.info(f"Call to write {prompt_name}...")
        msg['rc'] = 'Okay'
        msg['reason'] = f'Write of {prompt_name} Complete'
        # msg['record'] = msg['record']
        try:
            contents = msg['record']['text']
            if type(contents) is str:
                Step.memory[prompt_name] = contents
            else:
                Step.memory[prompt_name] = None
                self.memory_as_dictionary()
            # KbServerProtocol.log.info(f"Call to write {prompt_name} complete.")
        except KeyError as key:
            msg['rc'] = 'Fail'
            msg['reason'] = f'write of {prompt_name} Failed'
        self.send_object(msg)

    def create_directory(self, msg, isbinary):
        prompt_name = msg['record']['prompt_name']
        KbServerProtocol.log.info(f"Call to create_directory {prompt_name}...")
        msg['rc'] = 'Okay'
        msg['reason'] = f'create_directory {prompt_name} Complete'
        try:
            os.mkdir(f'{Step.memory.path}/{prompt_name}')
            KbServerProtocol.log.info(f"Call to create_directory {prompt_name} complete.")
        except KeyError as key:
            msg['rc'] = 'Fail'
            msg['reason'] = f'create_directory of {prompt_name} Failed {key}'
        self.send_object(msg)

    def delete_directory(self, msg, isbinary):
        prompt_name = msg['record']['prompt_name']
        KbServerProtocol.log.info(f"Call to delete_directory {prompt_name}...")
        msg['rc'] = 'Okay'
        msg['reason'] = f'delete_directory {prompt_name} Complete'
        try:
            shutil.rmtree(f'{Step.memory.path}/{prompt_name}')
            KbServerProtocol.log.info(f"Call to delete_directory {prompt_name} complete.")
        except KeyError as key:
            msg['rc'] = 'Fail'
            msg['reason'] = f'delete_directory of {prompt_name} Failed {key}'
        self.send_object(msg)

    def move_memory(self, msg, isbinary):
        from_path = msg['record']['from_path']
        to_path = msg['record']['to_path']
        KbServerProtocol.log.info(f"Call to move_memory {from_path} to {to_path}...")
        msg['rc'] = 'Okay'
        msg['reason'] = f"Call to move_memory {from_path} to {to_path}..."

        try:
            contents = Step.memory.read(from_path)
            # KbServerProtocol.log.info(f"read {from_full_name}: {contents}")
            Step.memory[to_path] = contents
            # KbServerProtocol.log.info(f"write {to_full_name}: {contents[:100]}")
            del Step.memory[from_path]
            KbServerProtocol.log.info(f"Call to move_memory {from_path} to {to_path}... complete")
        except KeyError as key:
            msg['rc'] = 'Fail'
            msg['reason'] = f'move failed key error {key}'
        self.send_object(msg)

    def move_step(self, msg, isbinary):
        from_process = msg['record']['from_process']
        from_step_no = msg['record']['from_step_no']
        to_process = msg['record']['to_process']
        to_step_no = msg['record']['to_step_no']

        KbServerProtocol.log.info(f"Call to move_step From {from_process}::{from_step_no}  to {to_process}::{to_step_no}...")

        msg['rc'] = 'Okay'
        msg['reason'] = f"Call to move_step complete"


        try:
            step = ProcessList[from_process].pop(from_step_no)
            ProcessList[to_process].insert(to_step_no, step)
            ProcessList_save(ProcessList)
            KbServerProtocol.log.info(f"Call to move_step From {from_process}::{from_step_no}  to {to_process}::{to_step_no}... complete")
        except KeyError as key:
            msg['rc'] = 'Fail'
            msg['reason'] = f'move_step failed key error {key}'
        self.send_object(msg)
        self.process_list_initial_load()

    def move_directory(self, msg, isbinary):
        prompt_name = msg['record']['prompt_name']
        from_path = msg['record']['from_path']
        to_path = msg['record']['to_path']
        KbServerProtocol.log.info(f"Call to move_directory {prompt_name} from {from_path} to {to_path}...")
        msg['rc'] = 'Okay'
        msg['reason'] = f"Call to move_directory {prompt_name} from {from_path} to {to_path} complete"

        try:
            from_full_name = f'{from_path}/{prompt_name}'
            to_full_name = f'{to_path}/{prompt_name}'
            shutil.move(from_full_name, to_full_name)
            KbServerProtocol.log.info(f"Call to move_directory {prompt_name} from {from_path} to {to_path} complete")
        except KeyError as key:
            msg['rc'] = 'Fail'
            msg['reason'] = f'move failed key error {key}'
        self.send_object(msg)
        self.memory_initial_load() # as I don't trust the iNotify to get this one right

    def delete_dynamic_memory(self, msg, isbinary):
        KbServerProtocol.log.info("Enter delete_dynamic_memory({msg})", msg=msg)
        full_path_name = msg['record']['full_path_name']
        KbServerProtocol.log.info(f"Call to delete_dynamic_memory({full_path_name})")
        msg['rc'] = 'Okay'
        msg['reason'] = f'Delete of dynamic_memory {full_path_name} Complete'
        Step.memory.clear_dynamic_memory(full_path_name)
        self.send_object(msg)
        self.memory_initial_load()
        # returnValue('')

    def delete_memory_backup(self, msg, isbinary):
        KbServerProtocol.log.info("Enter delete_memory_backup({msg})", msg=msg)
        full_path_name = msg['record']['full_path_name']
        KbServerProtocol.log.info(f"Call to delete_memory_backup({full_path_name})")
        msg['rc'] = 'Okay'
        msg['reason'] = f'Delete of delete_memory_backup {full_path_name} Complete'
        Step.memory.delete_memory_backup(full_path_name)
        self.send_object(msg)
        self.memory_initial_load()
        # returnValue('')

    def delete_memory(self, msg, isbinary):
        KbServerProtocol.log.info("Enter delete_memory({msg})", msg=msg)
        full_path_name = msg['record']['full_path_name']
        KbServerProtocol.log.info(f"Call to delete_memory({full_path_name})")
        msg['rc'] = 'Okay'
        msg['reason'] = f'Delete of memory {full_path_name} Complete'
        del Step.memory[full_path_name]
        self.send_object(msg)
        # self.memory_initial_load()  Memory is auto updated
        # returnValue('')

    def write_step(self, msg, isbinary):
        process_name = msg['record']['process_name']
        new_step = msg['record']['step']
        step_name = msg['record']['step_name']
        KbServerProtocol.log.info(f"Call to write step {process_name}::{step_name}...")
        msg['rc'] = 'Okay'
        msg['reason'] = f'Write of step {process_name}::{step_name} Complete'
        tasklist: List[Step] = ProcessList[process_name]
        for idx, step in enumerate(tasklist):
            if step.name == step_name:
                tasklist[idx] = Step.from_json(new_step)
                break
        ProcessList_save(ProcessList)
        KbServerProtocol.log.info(f"Call to write step {process_name}::{step_name}...")
        self.send_object(msg)
        self.process_list_initial_load()

    def create_step(self, msg, isbinary):
        empty_step = jsonpickle.loads(empty_step_json)  # This creates a new Object... Which avoids sharing problems
        process_name = msg['record']['process_name']
        step_index = msg['record']['step_index']
        step_name = msg['record']['step_name']
        KbServerProtocol.log.info(f"Call to create step {process_name}::{step_name}...")
        msg['rc'] = 'Okay'
        msg['reason'] = f'Create step {process_name}::{step_name} Complete'
        empty_step.name = step_name
        ProcessList[process_name].insert(step_index, empty_step)
        ProcessList_save(ProcessList)
        KbServerProtocol.log.info(f"Call to create_step {process_name}::{step_name}...")
        self.send_object(msg)
        self.process_list_initial_load()

    def rename_process(self, msg, isbinary):
        process_old_name = msg['record']['process_old_name']
        process_new_name = msg['record']['process_new_name']
        msg['rc'] = 'Okay'
        msg['reason'] = f'rename_process({process_old_name}, {process_new_name})... Complete'
        ProcessList[process_new_name] = ProcessList[process_old_name]
        del ProcessList[process_old_name]
        ProcessList_save(ProcessList)
        KbServerProtocol.log.info("Call rename_process({msg})... Complete", msg=msg)
        self.send_object(msg)

    def delete_process(self, msg, isbinary):
        process_name = msg['record']['process_name']
        msg['rc'] = 'Okay'
        msg['reason'] = f'delete_process({process_name})... Complete'
        del ProcessList[process_name]
        ProcessList_save(ProcessList)
        KbServerProtocol.log.info("Call delete_process({msg})... Complete", msg=msg)
        self.process_list_initial_load()
        self.send_object(msg)

    def create_process(self, msg, isbinary):
        process_name = msg['record']['process_name']
        msg['rc'] = 'Okay'
        msg['reason'] = f'create_process({process_name})... Complete'
        ProcessList[process_name] = []
        ProcessList_save(ProcessList)
        KbServerProtocol.log.info("Call create_process({msg})... Complete", msg=msg)
        self.send_object(msg)
        self.process_list_initial_load()

    def delete_step(self, msg, isbinary):
        KbServerProtocol.log.info("Enter delete_step({msg})", msg=msg)
        process_name = msg['record']['process_name']
        step_name = msg['record']['step_name']
        KbServerProtocol.log.info(f"Call to delete_step({process_name}, {step_name})")
        msg['rc'] = 'Okay'
        msg['reason'] = f'Delete of step {process_name}::{step_name} Complete'
        tasklist: List[Step] = ProcessList[process_name]
        for idx, step in enumerate(tasklist):
            if step.name == step_name:
                del tasklist[idx]
                break
        ProcessList_save(ProcessList)
        self.send_object(msg)
        self.process_list_initial_load()
        # returnValue('')

    @inlineCallbacks
    def onMessage(self, payload, isbinary):
        if not self.loggedIn:
            yield self.user_login(payload, isbinary)
            returnValue('')

        msg = json.loads(payload.decode('utf8'))
        method_name = f"{msg['cmd']}_{msg['object']}"
        # Check if the method exists in the instance and call it with parameters
        if hasattr(self, method_name):
            # KbServerProtocol.log.info("received msg calling {method_name}(...)", method_name=method_name)
            method = getattr(self, method_name)
            try:
                yield method(msg, isbinary)
            except Exception as err:
                tb = traceback.extract_tb(err.__traceback__)
                filename, line_number, function_name, text = tb[-1]
                print()
                KbServerProtocol.log.error("Error calling {method_name}(...): {err}", method_name=method_name, err=err)
                KbServerProtocol.log.error("Error occurred in {filename} on line {line_number}: {text}",
                                           filename=filename,  line_number=line_number, text=text)
                msg['rc'] = 'Fail'
                msg['reason'] = f'{method_name}(...) Failed: {err}'
                self.send_object(msg)

            returnValue('')

        # SQL Database Access - Not Used Yet
        # try:
        #     yield self.factory.db.make_change(msg=msg)
        # except Exception as err:
        #     KbServerProtocol.log.error("message not processed...reason({err})", err=err)
        #     msg['rc'] = 'Fail'
        #     msg['reason'] = f"message not processed...reason({err})"

        KbServerProtocol.log.error("received msg method not defined {method_name}(...)", method_name=method_name)
        msg['rc'] = 'Fail'
        msg['reason'] = f"Server msg method not defined {method_name}(...)"
        self.send_object(msg)
        returnValue('')

    def send_object(self, msg):
        response = json.dumps(msg, ensure_ascii=False)
        self.sendMessage(response.encode('UTF8'), False)


from twisted.internet import inotify
from twisted.python import filepath


def notify(_, fp, mask):
    """
    @param _: For historical reasons, an opaque handle is passed as first parameter. This object should never be used.
    @param fp: FilePath on which the event happened.
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

    # print(f"In Notify m:{m} have fp {type(fp)}  isdir(){fp.isdir()}")
    if 'delete' in m:
        content = ''
    elif 'is_dir' in m:
        content = ''
    elif 'delete_self' in m:
        content = ''
    else:
        content = fp.getContent().decode('utf-8')

    # print(f"event {', '.join(m)} on {'/'.join(p)}/{n}: {content[:80]}")
    msg = {'cmd': 'memory_update',
           'cb': 'memory_update',
           'rc': 'Okay',
           'object': 'memory',
           'record': {
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
