from __future__ import annotations

from typing import List

from openai import AsyncOpenAI

from .base import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: str, base_url: str) -> None:
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    async def chat(self, messages: List[dict], model: str, n: int = 1, temperature: float = 0.7) -> List[str]:
        response = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            n=n,
            temperature=temperature,
        )
        return [choice.message.content.strip() for choice in response.choices if choice.message.content]
