from typing import Any

from chatarena.backends import OpenAIChat


class Parser:
    def __init__(self) -> None:
        self.backend = OpenAIChat()
        self.backend.temperature = 0.0

    def __call__(self, prompt: str) -> Any:
        messages = [
            {"role": "system", "content": 'You are a helpful assistant'},
            {"role": "user", "content": prompt}
            ]
        return self.backend._get_response(messages)
