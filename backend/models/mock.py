from __future__ import annotations

import random
from typing import List

from .base import BaseLLMProvider


class MockProvider(BaseLLMProvider):
    async def chat(self, messages: List[dict], model: str, n: int = 1, temperature: float = 0.7) -> List[str]:
        seed = abs(hash("".join(m.get("content", "") for m in messages))) % 10000
        random.seed(seed)
        templates = [
            "What assumptions are you making about the loop boundaries?",
            "Which variable changes each iteration, and could it skip the last element?",
            "If you trace the smallest input by hand, where does it diverge from expectation?",
            "What is the first place an index could be out of range?",
            "Can you print the values just before the error to confirm the state?",
        ]
        return random.sample(templates, k=min(n, len(templates)))
