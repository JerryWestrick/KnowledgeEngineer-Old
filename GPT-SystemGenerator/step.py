# This class represents a single step in an AI workflow.
# It is a singleton.
#
# The name of the step is the key to the dictionary
import json
import re
import time

from ai import AI
from db import DB
from logger import Logger


def interpret_results(text: str) -> dict[str, str]:
    """
    Search Text for Text Blocks and add them as files to the Memory
    """
    # text_block_pattern = re.compile()

    result = {}
    full_path: str = ''
    content: str = ''
    text_blocks = re.findall(r'^([\w\s/:.]+)```([^`]+)```', text, re.MULTILINE)
    for (name, content) in text_blocks:
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

    def __init__(self, name: str, prompt_name: str, ai: AI, storage_path: str):
        # Note:  If you recreate a new step will overwrite the old one.
        self.name: str = name
        self.prompt_name: str = prompt_name
        self.ai: AI = ai
        self.storage_path: str = storage_path
        self.__class__.instances[name] = self
        # Storage for historical values
        self.messages: [dict[str, str]] = []        # The messages that have been sent to the AI
        self.response: dict = {}                    # The responses that have been received from the AI
        self.answer: str = ''                       # The answer from within the response
        self.files: dict[str, str] = {}             # The files that have been returned from the AI
        self.prompt_tokens: int = 0
        self.completion_tokens: int = 0
        self.total_tokens: int = 0
        self.elapsed_time: float = 0.0

    def run(self):
        head_len = len('[2023-06-30 10:29:41] STEP: ')
        head = ' ' * head_len
        Logger.log('STEP', f"{'=' * 50}\n{head}Begin Step: {self.name}\n{head}{self.prompt_name}")
        self.messages = self.memory[self.prompt_name]

        start_time = time.time()
        self.response = self.ai.generate(self.messages)
        self.elapsed_time = time.time() - start_time
        self.prompt_tokens = self.response['usage']['prompt_tokens']
        self.completion_tokens = self.response['usage']['completion_tokens']
        self.total_tokens = self.response['usage']['total_tokens']
        Logger.log('STEP', f"Call {self.ai.model} Elapsed: {self.elapsed_time:.2f}s Token Usage: "
                           f"Total:{self.total_tokens} ("
                           f"Prompt:{self.prompt_tokens}, "
                           f"Completion:{self.completion_tokens})"
                   )

        if self.ai.mode == 'chat':
            self.answer = self.response.choices[0].message.content
        else:
            self.answer = self.response.choices[0].text

        self.files = interpret_results(text=self.answer)

        # Okay Now we  need to save the response to the memory
        for name, content in self.files.items():
            # check for set memory
            if name == 'json':
                t = json.loads(content)
                for k, v in t.items():
                    self.memory.macro[k] = v
                    Logger.log('STEP', f"Setting Memory.macro['{k}']={v}")
                continue
            else:
                full_path = f"{self.storage_path}/{name}"
                self.memory[full_path] = content
                Logger.log('STEP', f"Writing {full_path}")

    @classmethod
    def __retrieve(cls, name):
        return cls.instances.get(name, None)

    def __getitem__(self, name):
        # This is meant to allow accessing the step by name
        # Directly on  the class.  i.e. Step['name']
        return self.__retrieve(name)
