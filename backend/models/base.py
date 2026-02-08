from __future__ import annotations

from typing import List


class BaseLLMProvider:
    async def chat(self, messages: List[dict], model: str, n: int = 1, temperature: float = 0.7) -> List[str]:
        raise NotImplementedError
