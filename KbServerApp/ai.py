from __future__ import annotations

import json
import os
import time

import openai
from dotenv import load_dotenv
from twisted.internet.defer import inlineCallbacks
from twisted.logger import Logger

import KbServerApp.colors

from KbServerApp.OpenAI_API_Costs import OpenAI_API_Costs
from KbServerApp.defered import as_deferred

load_dotenv()


class AI:
    log = Logger(namespace='AI')

    openai.api_key = os.getenv('OPENAI_API_KEY')
    models = openai.Model.list()

    @classmethod
    def list_models(cls):
        l: list[str] = []
        for m in cls.models.data:
            l.append(m['id'])
        return l

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
        self.answer: str = answer,
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
            openai.Model.retrieve(model)
        except openai.InvalidRequestError as e:
            AI.log.error(f"Error: {e}")
            AI.log.warn(
                       f"Model {model} not available for provided API key. Reverting "
                       "to text-davinci-003. Sign up for the GPT-4 wait list here: "
                       "https://openai.com/waitlist/gpt-4-api"
                       )
            self.model = "gpt-3.5-turbo"

        # GptLogger.log('SYSTEM', f"Using model {self.model} in mode {self.mode}")

    @inlineCallbacks
    def generate(self):
        # AI.log.info("generate()")
        self.answer = ''
        start_time = time.time()
        if self.mode == 'complete':
            prompt: str = ''
            for message in self.messages:
                prompt += message['content'] + '\n'
            ai_response = yield self.complete(prompt)
            self.answer = ai_response.choices[0].text

        elif self.mode == 'chat':
            ai_response = yield self.chat(self.messages)
            self.answer = ai_response.choices[0].message.content

        # Gather Answer
        self.e_stats['elapsed_time'] = time.time() - start_time
        pricing = OpenAI_API_Costs[self.model]

        self.e_stats['prompt_tokens'] = ai_response['usage']['prompt_tokens']
        self.e_stats['completion_tokens'] = ai_response['usage']['completion_tokens']
        self.e_stats['total_tokens'] = ai_response['usage']['total_tokens']

        self.e_stats['sp_cost'] = pricing['input'] * (self.e_stats['prompt_tokens'] / 1000)
        self.e_stats['sc_cost'] = pricing['output'] * (self.e_stats['completion_tokens'] / 1000)
        self.e_stats['s_total'] = self.e_stats['sp_cost'] + self.e_stats['sc_cost']

        return self.answer

    @inlineCallbacks
    def chat(self, messages: list[dict[str, str]]) -> dict:

        # AI.log.info(f"Calling {self.model} chat with messages: ")
        try:
            response = yield as_deferred(openai.ChatCompletion.acreate(
                messages=messages,
                model=self.model,
                temperature=self.temperature,
            ))
        except Exception as err:
            self.log.error("Call to ChatGpt returned error: {err}", err=err)
            raise

        # AI.log.info(f"{self.model} chat Response")
        return response

    @inlineCallbacks
    def complete(self, prompt: str) -> dict:

        # AI.log.info(f"Calling {self.model} complete with prompt: ")
        completion = yield as_deferred(openai.Completion.acreate(
            model=self.model,
            prompt=prompt,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        ))
        # AI.log.info(f"{self.model} Response")
        return completion

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


