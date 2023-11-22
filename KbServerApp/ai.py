from __future__ import annotations

import json
import os
from openai import AsyncOpenAI

from dotenv import load_dotenv
from twisted.internet import utils
from twisted.internet.defer import inlineCallbacks, succeed
from twisted.logger import Logger

from OpenAI_API_Costs import OpenAI_API_Costs
from db import DB
from defered import as_deferred

load_dotenv()


class AI:
    log = Logger(namespace='AI')
    memory = DB('Memory')
    # client = OpenAI()
    # client.api_key = os.getenv('OPENAI_API_KEY')
    # m = client.models.list()
    # models = m.data
    #
    client = AsyncOpenAI()
    client.api_key = os.getenv('OPENAI_API_KEY')


    # @classmethod
    # def list_models(cls):
    #     l: list[str] = []
    #     for m in cls.models.data:
    #         l.append(m['id'])
    #     return l

    def __init__(self,
                 model: str = "gpt-4",
                 temperature: float = 0,
                 max_tokens: int = 2000,
                 mode: str = 'complete',
                 messages: [dict[str, str]] = None,
                 answer: str = None,
                 files: dict[str, str] = None,
                 e_stats: dict[str, float] = None
                 ):
        self.temperature: float = temperature
        self.max_tokens: int = max_tokens
        self.model: str = model
        self.mode: str = mode
        self.messages: [dict[str, str]] = messages
        if messages is None:
            self.messages = []
        self.answer: str = answer
        if answer is None:
            self.messages = []

        self.files: dict[str, str] = files
        if files is None:
            self.files = {}

        self.e_stats: dict[str, float] = e_stats
        if e_stats is None:
            self.e_stats = {
                'prompt_tokens': 0.0,
                'completion_tokens': 0.0,
                'total_tokens': 0.0,
                'sp_cost': 0.0,
                'sc_cost': 0.0,
                's_total': 0.0,
                'elapsed_time': 0.0,
            }

        try:
            AI.client.models.retrieve(model)
        except Exception as e:
            AI.log.error(f"Error: {e}")
            AI.log.warn(
                f"Model {model} not available for provided API key. Reverting "
                "to gpt-3.5-turbo. Sign up for the GPT-4 wait list here: "
                "https://openai.com/waitlist/gpt-4-api"
            )
            self.model = "gpt-3.5-turbo"

        # GptLogger.log('SYSTEM', f"Using model {self.model} in mode {self.mode}")

    @inlineCallbacks
    def read_file(self, name: str):

        try:
            file_msgs = self.memory[name]

        except Exception as err:
            self.log.error("Error while reading file for AI...")
            result = yield succeed({'role': 'function', 'name': 'read_file', 'content': f'ERROR file not found: {name}'})
            return result

        file_msg = file_msgs[0]
        file_contents = file_msg['content']
        result = yield succeed({'role': 'function', 'name': 'read_file', 'content': file_contents})
        return result

    @inlineCallbacks
    def write_file(self, name: str, contents: str):
        try:
            self.memory[name] = contents
        except Exception as err:
            self.log.error("Error while writing file for AI...")
            raise
        self.log.info("Writing<<{name}", name=name)
        result = yield succeed({'role': 'function', 'name': 'write_file', 'content': 'Done.'})
        return result

    @inlineCallbacks
    def patch_file(self, file_name: str, patch_name: str, contents: str) -> dict[str, str]:
        self.memory[patch_name] = contents

        # Get directory of file to update
        directory = os.path.dirname(file_name)

        # Command to apply the patch
        cmd = f"patch < {patch_name}"
        msg = ''
        try:
            stdout, stderr, exitcode = yield utils.getProcessOutputAndValue(
                "/bin/sh",
                args=["-c", cmd],
                path=directory)
            if exitcode == 0:
                msg = stdout.decode()
            else:
                msg = stderr.decode()
        except Exception as err:
            self.log.error("Error while writing patch file for AI...{msg}", msg=msg)
            msg = f"Exception applying patch_file {patch_name}: {err}"

        self.log.info("Patch<<{name} {msg}", name=patch_name, msg=msg)

        return {'role': 'function', 'name': 'patch_file', 'content': msg}

    functions = [
        {
            "name": "read_file",
            "description": "Read the contents of a named file",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name of the file to read",
                    },
                },
                "required": ["name"],
            },
        },
        {
            "name": "write_file",
            "description": "Write the contents to a named file",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name of the file to write",
                    },
                    "contents": {
                        "type": "string",
                        "description": "The contents of the file",
                    },
                },
                "required": ["name", "contents"],
            },
        },
        {
            "name": "patch_file",
            "description": "Run Patch file",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_name": {
                        "type": "string",
                        "description": "The name of the file to be patched",
                    },
                    "patch_name": {
                        "type": "string",
                        "description": "The name of the patch to be applied",
                    },
                    "contents": {
                        "type": "string",
                        "description": "The contents of the patch file",
                    },
                },
                "required": ["file_name", "patch_name", "contents"],
            },
        }
    ]
    available_functions = {
        "read_file": read_file,
        "write_file": write_file,
        "patch_file": patch_file,
    }

    @inlineCallbacks
    def generate(self, step, user_messages: list[dict[str, str]]) -> dict[str, str]:

        self.answer = f'Log of Step: {step.name} : {step.prompt_name}\n'
        pricing = OpenAI_API_Costs[self.model]

        while user_messages:
            msg = user_messages.pop(0)
            if msg['role'] != 'exec':
                self.messages.append(msg)
                self.log.info("    --> msg:{msg}", msg=msg)
                continue

            repeat = True
            while repeat:
                repeat = False

                step.update_gui()
                ai_response = yield self.chat(self.messages)
                response_message = {'role': ai_response.choices[0].message.role,
                                    'content': ai_response.choices[0].message.content
                                    }
                function_name = None
                function_args = None
                if ai_response.choices[0].finish_reason == 'function_call':
                    # if ai_response.choices[0].message.get("function_call"):
                    function_call = ai_response.choices[0].message.function_call
                    function_name = function_call.name
                    function_args = json.loads(function_call.arguments)
                    response_message['function_call'] = {'name': function_name, 'arguments': function_call.arguments}
                else:
                    self.answer = f"{self.answer}\n\n - {response_message['content']}"

                self.messages.append(response_message)
                self.log.info("    <-- msg:{msg}", msg=response_message)  # Display with last message
                if ai_response.choices[0].finish_reason == 'function_call':
                    new_msg = yield self.available_functions[function_name](self, **function_args)
                    self.messages.append(new_msg)
                    self.log.info("    --> msg:{msg}", msg=new_msg)
                    repeat = True
                else:
                    lines = response_message['content'].split("\n")
                    if lines[-1].lower().endswith("continue?"):
                        repeat = True
                        self.messages.append({'role': 'User', 'content': 'Continue.'})

                # Gather Answer
                self.e_stats['prompt_tokens'] = \
                    self.e_stats['prompt_tokens'] + ai_response.usage.prompt_tokens
                self.e_stats['completion_tokens'] = \
                    self.e_stats['completion_tokens'] + ai_response.usage.completion_tokens

        self.e_stats['sp_cost'] = pricing['input'] * (self.e_stats['prompt_tokens'] / 1000.0)
        self.e_stats['sc_cost'] = pricing['output'] * (self.e_stats['completion_tokens'] / 1000.0)
        self.e_stats['s_total'] = self.e_stats['sp_cost'] + self.e_stats['sc_cost']

        return self.answer

    @inlineCallbacks
    def chat(self, messages: list[dict[str, str]]) -> dict:

        # AI.log.info(f"Calling {self.model} chat with messages: ")
        try:
            response = yield as_deferred(AI.client.chat.completions.create(
                messages=messages,
                model=self.model,
                temperature=self.temperature,
                functions=self.functions,
                function_call="auto")
            )
            # messages = messages,
            # model = self.model,
            # temperature = self.temperature,
            # tools = self.functions,
            # tools_choice = "auto"
        except Exception as err:
            self.log.error("Call to ChatGpt returned error: {err}", err=err)
            raise

        # AI.log.info(f"{self.model} chat Response")
        return response

    def to_json(self) -> dict:
        return {
            'model': self.model,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'mode': self.mode,
            'messages': self.messages,
            'answer': self.answer,
            'files': self.files,
            'e_stats': self.e_stats
        }

    @classmethod
    def from_json(cls, param) -> AI:
        return cls(**param)


if __name__ == "__main__":
    print(f"Models: {len(OpenAI_API_Costs)}")
    for m in sorted(OpenAI_API_Costs):
        print(f'\t{OpenAI_API_Costs[m]}')