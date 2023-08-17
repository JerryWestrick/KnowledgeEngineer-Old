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

    def __init__(self, name: str, prompt_name: str, ai: AI, storage_path: str, text_file: str):
        # Note:  If you recreate a new step will overwrite the old one.
        self.name: str = name
        self.prompt_name: str = prompt_name
        self.storage_path: str = storage_path
        self.text_file: str = text_file
        # Storage for historical values
        self.ai: AI = ai
        self.messages: [dict[str, str]] = []  # The messages that have been sent to the AI
        self.answer: str = ''  # The answer from within the response
        self.files: dict[str, str] = {}  # The files that have been returned from the AI
        self.e_stats: dict[str, float] = {
            'prompt_tokens': 0.0,
            'completion_tokens': 0.0,
            'total_tokens': 0.0,
            'sp_cost': 0.0,
            'sc_cost': 0.0,
            's_total': 0.0,
            'elapsed_time': 0.0,
        }  # The execution statistics for the AI

    def to_json(self) -> dict:
        """
        Convert the Step to a JSON object
        """
        return {
            'name': self.name,
            'prompt_name': self.prompt_name,
            'storage_path': self.storage_path,
            'text_file': self.text_file,
            'ai': self.ai.to_json(),
        }

    @classmethod
    def from_json(cls, json_obj: dict) -> 'Step':
        """
        Create a Step from a JSON object
        """
        step = cls(
            name=json_obj['name'],
            prompt_name=json_obj['prompt_name'],
            ai=AI.from_json(json_obj['ai']),
            storage_path=json_obj['storage_path'],
            text_file=json_obj['text_file']
        )
        return step

    @inlineCallbacks
    def run(self, proto, pname):
        msg = {}
        head_len = len('[2023-06-30 10:29:41] STEP: ')
        head = ' ' * head_len
        Step.log.info(f"{'=' * 50}\n{head}Begin Step: {self.name}\n{head}{self.prompt_name}")
        self.ai.messages = self.memory[self.prompt_name]
        # Clear Old History
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
        msg = {'cmd': 'update', 'cb': 'update_step', 'rc': 'Okay', 'object': 'step', 'record': self.to_json()}
        response = json.dumps(msg, ensure_ascii=False, default=str)
        proto.sendMessage(response.encode('UTF8'), False)

        start_time = time.time()
        ai_response = yield self.ai.generate()
        Step.log.info(f"Call {self.ai.model} Elapsed: {self.ai.e_stats['elapsed_time']:.2f}s Token Usage: "
                      f"Total:{self.ai.e_stats['total_tokens']} ("
                      f"Prompt:{self.ai.e_stats['prompt_tokens']}, "
                      f"Completion:{self.ai.e_stats['completion_tokens']})")

        self.ai.files = interpret_results(text=self.ai.answer)
        # Send Update to the GUI
        msg = {'cmd': 'update', 'cb': 'update_step', 'rc': 'Okay', 'object': 'step', 'record': self.to_json()}
        response = json.dumps(msg, ensure_ascii=False, default=str)
        proto.sendMessage(response.encode('UTF8'), False)

        # Okay Now we  need to save the response to the memory
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
