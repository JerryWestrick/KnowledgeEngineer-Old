from __future__ import annotations
import os
import openai
from dotenv import load_dotenv

import colors
from logger import Logger

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
            Logger.log('SYSTEM', f"Error: {e}")
            Logger.log('WARNNIG',
                f"Model {model} not available for provided API key. Reverting "
                "to text-davinci-003. Sign up for the GPT-4 wait list here: "
                "https://openai.com/waitlist/gpt-4-api"
            )
            self.model = "text-davinci-003"

        # Logger.log('SYSTEM', f"Using model {self.model} in mode {self.mode}")

    def generate(self, messages: list[dict[str, str]]) -> dict:
        if self.mode == 'complete':
            prompt: str = ''
            for message in messages:
                prompt += message['content'] + '\n'
            return self.complete(prompt)

        elif self.mode == 'chat':
            return self.chat(messages)

    def chat(self, messages: list[dict[str, str]]) -> dict:

        Logger.log("LLM", f"Calling {self.model} chat with messages: ")
        if Logger.logging_actions['PROMPT']:
            prompt: str = ''
            for message in messages:
                prompt += f"{message['role']}:\n{message['content']} \n"
            Logger.log("PROMPT", prompt)

        response = openai.ChatCompletion.create(
            messages=messages,
            model=self.model,
            temperature=self.temperature,
        )

        Logger.log("RESPONSE", f"{self.model} chat Response: \n{response.choices[0].message.content}")
        return response

    def complete(self, prompt: str) -> dict:

        Logger.log("LLM", f"Calling {self.model} complete with prompt: ")
        Logger.log("PROMPT", f"{prompt}")
        completion = openai.Completion.create(
            model=self.model,
            prompt=prompt,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )
        Logger.log("RESPONSE", f"{self.model} Response: \n{completion.choices[0].text}")
        return completion
