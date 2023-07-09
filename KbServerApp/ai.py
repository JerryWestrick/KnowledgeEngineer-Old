from __future__ import annotations
import os
import openai
from dotenv import load_dotenv
from twisted.internet.defer import inlineCallbacks

import KbServerApp.colors
from KbServerApp.logger import GptLogger
from KbServerApp.defered import as_deferred

load_dotenv()


class AI:
    openai.api_key = os.getenv('OPENAI_API_KEY')
    models = openai.Model.list()

    @classmethod
    def list_models(cls):
        l: list[str] = []
        for m in cls.models.data:
            l.append(m['id'])
        return l

    def __init__(self, model: str = "gpt-4", temperature: float = 0, max_tokens: int = 2000, mode: str = 'complete'):
        self.temperature: float = temperature
        self.max_tokens: int = max_tokens
        self.model: str = model
        self.mode: str = mode

        try:
            openai.Model.retrieve(model)
        except openai.InvalidRequestError as e:
            GptLogger.log('SYSTEM', f"Error: {e}")
            GptLogger.log('WARNNIG',
                       f"Model {model} not available for provided API key. Reverting "
                       "to text-davinci-003. Sign up for the GPT-4 wait list here: "
                       "https://openai.com/waitlist/gpt-4-api"
                       )
            self.model = "text-davinci-003"

        # GptLogger.log('SYSTEM', f"Using model {self.model} in mode {self.mode}")

    @inlineCallbacks
    def generate(self, messages: list[dict[str, str]]):
        response = ''
        if self.mode == 'complete':
            prompt: str = ''
            for message in messages:
                prompt += message['content'] + '\n'
            response = yield self.complete(prompt)
            return response

        elif self.mode == 'chat':
            response = yield self.chat(messages)
            return response

    @inlineCallbacks
    def chat(self, messages: list[dict[str, str]]) -> dict:

        GptLogger.log("LLM", f"Calling {self.model} chat with messages: ")
        if GptLogger.gpt_logging_actions['PROMPT']:
            prompt: str = ''
            for message in messages:
                prompt += f"{message['role']}:\n{message['content']} \n"
            GptLogger.log("PROMPT", prompt)

        response = yield as_deferred(openai.ChatCompletion.acreate(
            messages=messages,
            model=self.model,
            temperature=self.temperature,
        ))

        GptLogger.log("RESPONSE", f"{self.model} chat Response: \n{response.choices[0].message.content}")
        return response

    @inlineCallbacks
    def complete(self, prompt: str) -> dict:

        GptLogger.log("LLM", f"Calling {self.model} complete with prompt: ")
        GptLogger.log("PROMPT", f"{prompt}")
        completion = yield as_deferred(openai.Completion.acreate(
            model=self.model,
            prompt=prompt,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        ))
        GptLogger.log("RESPONSE", f"{self.model} Response: \n{completion.choices[0].text}")
        return completion

    def to_json(self) -> dict:
        return {
            'model': self.model,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'mode': self.mode
        }

    @classmethod
    def from_json(cls, param) -> AI:
        return cls(**param)


