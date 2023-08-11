# This class represents a single step in an AI workflow.
# It is a singleton.
#
# The name of the step is the key to the dictionary
import json
import re
import time

from twisted.internet.defer import inlineCallbacks

from KbServerApp.OpenAI_API_Costs import OpenAI_API_Costs
from KbServerApp.ai import AI
from KbServerApp.db import DB
from KbServerApp.logger import GptLogger


def interpret_results(text: str) -> dict[str, str]:
    """
    Search Text for Text Blocks and add them as files to the Memory
    """
    # text_block_pattern = re.compile()

    result = {}
    full_path: str = ''
    content: str = ''
    text_blocks = re.findall(r'^([\w\s/:.]+)```(\w+)?([^`]+)```', text, re.MULTILINE)
    for (name, ext, content) in text_blocks:
        name = name.strip()
        content = content.strip()

        # remove the file extension if it is '.xxx.pe'
        pl = name.split('.')
        if pl[-1] == 'pe' and len(pl[-2]) < 5:
            pl.pop()  # remove the file extension
            name = '.'.join(pl)

        result[name] = content
    return result


class Step:
    instances = {}
    memory = DB('Memory')

    def __init__(self, name: str, prompt_name: str, ai: AI, storage_path: str, text_file: str):
        # Note:  If you recreate a new step will overwrite the old one.
        self.name: str = name
        self.prompt_name: str = prompt_name
        self.ai: AI = ai
        self.storage_path: str = storage_path
        self.text_file: str = text_file
        self.__class__.instances[name] = self
        # Storage for historical values
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
            'ai': self.ai.to_json(),
            'storage_path': self.storage_path,
            'messages': self.messages,
            'answer': self.answer,
            'files': self.files,
            'text_file': self.text_file,
            'e_stats': {
                'prompt_tokens': self.e_stats['prompt_tokens'],
                'completion_tokens': self.e_stats['completion_tokens'],
                'total_tokens': self.e_stats['total_tokens'],
                'sp_cost': self.e_stats['sp_cost'],
                'sc_cost': self.e_stats['sc_cost'],
                's_total': self.e_stats['s_total'],
                'elapsed_time': self.e_stats['elapsed_time'],
            }
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
        if 'messages' not in json_obj:
            return step
        step.messages = json_obj['messages']
        step.answer = json_obj['answer']
        step.files = json_obj['files']
        step.e_stats = json_obj['e_stats']
        return step

    @inlineCallbacks
    def run(self, proto, pname):
        msg = {}
        head_len = len('[2023-06-30 10:29:41] STEP: ')
        head = ' ' * head_len
        GptLogger.log('STEP', f"{'=' * 50}\n{head}Begin Step: {self.name}\n{head}{self.prompt_name}")
        self.messages = self.memory[self.prompt_name]
        # clear old History...
        self.answer = ''
        self.files = {}
        self.e_stats['elapsed_time'] = 0.0
        self.e_stats['prompt_tokens'] = 0.0
        self.e_stats['completion_tokens'] = 0.0
        self.e_stats['sp_cost'] = 0.0
        self.e_stats['sc_cost'] = 0.0
        self.e_stats['s_total'] = 0.0
        self.e_stats['elapsed_time'] = 0.0

        # Send Update to the GUI
        msg = {'cmd': 'update', 'cb': 'update_step', 'rc': 'Okay', 'object': 'step', 'record': self.to_json()}
        response = json.dumps(msg, ensure_ascii=False, default=str)
        proto.sendMessage(response.encode('UTF8'), False)

        start_time = time.time()
        ai_response = yield self.ai.generate(self.messages)
        self.e_stats['elapsed_time'] = time.time() - start_time
        self.e_stats['prompt_tokens'] = ai_response['usage']['prompt_tokens']
        self.e_stats['completion_tokens'] = ai_response['usage']['completion_tokens']
        self.e_stats['total_tokens'] = ai_response['usage']['total_tokens']
        GptLogger.log('STEP', f"Call {self.ai.model} Elapsed: {self.e_stats['elapsed_time']:.2f}s Token Usage: "
                              f"Total:{self.e_stats['total_tokens']} ("
                              f"Prompt:{self.e_stats['prompt_tokens']}, "
                              f"Completion:{self.e_stats['completion_tokens']})"
                      )

        if self.ai.mode == 'chat':
            self.answer = ai_response.choices[0].message.content
        else:
            self.answer = ai_response.choices[0].text

        self.files = interpret_results(text=self.answer)
        pricing = OpenAI_API_Costs[self.ai.model]

        self.e_stats['sp_cost'] = pricing['input'] * (self.e_stats['prompt_tokens'] / 1000)
        self.e_stats['sc_cost'] = pricing['output'] * (self.e_stats['completion_tokens'] / 1000)
        self.e_stats['s_total'] = self.e_stats['sp_cost'] + self.e_stats['sc_cost']

        # Send Update to the GUI
        msg = {'cmd': 'update', 'cb': 'update_step', 'rc': 'Okay', 'object': 'step', 'record': self.to_json()}
        response = json.dumps(msg, ensure_ascii=False, default=str)
        proto.sendMessage(response.encode('UTF8'), False)

        # Okay Now we  need to save the response to the memory
        for name, content in self.files.items():
            # check for set memory
            if name == 'variable':
                t = json.loads(content)
                for k, v in t.items():
                    self.memory.macro[k] = v
                    GptLogger.log('STEP', f"Setting Memory.macro['{k}']={v}")
                continue
            else:
                full_path = f"{self.storage_path}/{name}"
                self.memory[full_path] = content
                GptLogger.log('STEP', f"Writing {full_path}")
        if self.text_file != '':
            full_path = f"{self.storage_path}/{self.text_file}"
            self.memory[full_path] = self.answer
            GptLogger.log('STEP', f"Writing {full_path}")


    