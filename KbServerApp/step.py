# This class represents a single step in an AI workflow.
# It is a singleton.
#
# The name of the step is the key to the dictionary
import json
import re
import time


from twisted.internet.defer import inlineCallbacks
from twisted.logger import Logger

from KbServerApp.ai import AI
from KbServerApp.db import DB


def interpret_results(text: str) -> dict[str, str]:
    """
    Search Text for Text Blocks and add them as files to the Memory
    """
    # text_block_pattern = re.compile()

    result = {}
    full_path: str = ''
    content: str = ''
    # text_blocks = re.findall(r'^([\w\s/:.]+)```(\w+)?([^`]+)```', text, re.MULTILINE)
    text_blocks = re.findall(r"^(\w[\w ]+)\.(.+)$\n^```(.*)$\n((?:^(?!```).*$\n?)+)^```", text, re.MULTILINE)
    for (name, ext, _, content) in text_blocks:
        name = name.strip()
        name = name.replace("*", "")
        ext = ext.replace("*", "")
        content = content.strip()
        file_name = f"{name}.{ext}"

        # remove the file extension if it is '.xxx.pe'
        pl = file_name.split('.')
        if pl[-1] == 'pe' and len(pl[-2]) < 5:
            pl.pop()  # remove the file extension
            file_name = '.'.join(pl)

        result[file_name] = content
    return result


class Step:
    log = Logger(namespace='Step')
    memory = DB('Memory')

    def __init__(self, name: str, prompt_name: str, ai: AI, storage_path: str = '', text_file: str = '',
                 file_process_enabled: bool = False, file_process_name: str = '', file_glob: str = '',
                 macros: dict[str, str] = None):
        self.name: str = name
        self.prompt_name: str = prompt_name
        self.storage_path: str = storage_path
        self.text_file: str = text_file
        self.file_process_enabled: bool = file_process_enabled
        self.file_process_name: str = file_process_name
        self.file_glob: str = file_glob
        self.macros: dict[str, str] = macros
        if macros is None:
            self.macros = {}
        self.ai: AI = ai

    def to_json(self) -> dict:
        """
        Convert the Step to a JSON object
        """
        return {
            'name': self.name,
            'prompt_name': self.prompt_name,
            'storage_path': self.storage_path,
            'text_file': self.text_file,
            'file_process_enabled': self.file_process_enabled,
            'file_process_name': self.file_process_name,
            'file_glob': self.file_glob,
            'macros': self.macros,
            'ai': self.ai.to_json()
        }

    @classmethod
    def from_json(cls, json_obj: dict) -> 'Step':
        """
        Create a Step from a JSON object
        """
        step = cls(
            name=json_obj['name'],
            prompt_name=json_obj['prompt_name'],
            storage_path=json_obj['storage_path'],
            text_file=json_obj['text_file'],
            file_process_enabled=json_obj['file_process_enabled'],
            file_process_name=json_obj['file_process_name'],
            file_glob=json_obj['file_glob'],
            macros=json_obj['macros'],
            ai=AI.from_json(json_obj['ai'])
        )
        return step

    @inlineCallbacks
    def run(self, proto, pname):
        msg = {}
        head_len = len('[2023-06-30 10:29:41] STEP: ') + 22
        head = ' ' * head_len
        self.memory.macro = self.macros  # Use these values for macro substitution
        try:
            self.ai.messages = self.memory[self.prompt_name]
        except Exception as err:
            self.log.error("Error in self.memory[self.prompt_name] {err}", err=err)
            raise

        # Clear Old History
        # self.log.info("step.run()::1")
        self.ai.answer = ''
        self.ai.files = {}
        self.ai.e_stats['elapsed_time'] = 0.0
        self.ai.e_stats['prompt_tokens'] = 0.0
        self.ai.e_stats['completion_tokens'] = 0.0
        self.ai.e_stats['sp_cost'] = 0.0
        self.ai.e_stats['sc_cost'] = 0.0
        self.ai.e_stats['s_total'] = 0.0
        self.ai.e_stats['elapsed_time'] = 0.0

        # Send Update to the GUI
        # self.log.info("step.run()::2")
        msg = {'cmd': 'update', 'cb': 'update_step', 'rc': 'Okay', 'object': 'step', 'record': self.to_json()}
        # self.log.info("step.run()::3")
        response = json.dumps(msg, ensure_ascii=False, default=str)
        # self.log.info("step.run()::4")
        proto.sendMessage(response.encode('UTF8'), False)

        start_time = time.time()
        Step.log.info(f"{'=' * 50}\n{head}Begin Step: {pname}:{self.name} -- {self.prompt_name}")
        try:
            ai_response = yield self.ai.generate()
        except Exception as err:
            self.log.error(f"Error in ai.generate: {err}", err=err)
            raise

        Step.log.info(f"Call {self.ai.model} Elapsed: {self.ai.e_stats['elapsed_time']:.2f}s Token Usage: "
                      f"Total:{self.ai.e_stats['total_tokens']} ("
                      f"Prompt:{self.ai.e_stats['prompt_tokens']}, "
                      f"Completion:{self.ai.e_stats['completion_tokens']})")
        Step.log.info(f"End Step: {pname}:{self.name} -- {self.prompt_name}\n{head}{'=' * 50}")

        self.ai.files = interpret_results(text=self.ai.answer)
        # Send Update to the GUI
        msg = {'cmd': 'update', 'cb': 'update_step', 'rc': 'Okay', 'object': 'step', 'record': self.to_json()}
        response = json.dumps(msg, ensure_ascii=False, default=str)
        proto.sendMessage(response.encode('UTF8'), False)

        # Okay Now we need to save the response to the memory
        for name, content in self.ai.files.items():
            # check for set memory
            if name == 'variable':
                t = json.loads(content)
                for k, v in t.items():
                    self.memory.macro[k] = v
                    Step.log.info(f"Setting Memory.macro['{k}']={v}")
                continue
            else:
                full_path = f"{self.storage_path}/{name}"
                self.memory[full_path] = content
                Step.log.info(f"Writing {full_path}")
        if self.text_file != '':
            full_path = f"{self.storage_path}/{self.text_file}"
            self.memory[full_path] = self.ai.answer
            Step.log.info(f"Writing {full_path}")
