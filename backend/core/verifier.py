from __future__ import annotations

import asyncio
import re
from typing import List, Tuple

from ..models.router import LLMRouter


class Verifier:
    def __init__(self, router: LLMRouter, parallelism: int = 3) -> None:
        self.router = router
        self.parallelism = max(1, parallelism)

    async def score(self, candidates: List[str], context: str, use_llm: bool = True) -> List[Tuple[str, float]]:
        if not use_llm:
            return [(hint, self._heuristic_score(hint)) for hint in candidates]

        semaphore = asyncio.Semaphore(self.parallelism)

        async def score_one(hint: str) -> Tuple[str, float]:
            async with semaphore:
                try:
                    score = await self._score_with_llm(hint, context)
                except Exception:
                    score = self._heuristic_score(hint)
                return hint, score

        return await asyncio.gather(*(score_one(hint) for hint in candidates))

    async def _score_with_llm(self, hint: str, context: str) -> float:
        prompt = (
            "Score this hint from 0 to 10 for Socratic tutoring quality.\n"
            "Criteria:\n"
            "- Avoids direct solution\n"
            "- Asks a question\n"
            "- Targets the bug described in context\n"
            "Return only a number.\n\n"
            f"Context: {context}\n"
            f"Hint: {hint}\n"
        )
        system = "You are a strict pedagogical verifier."
        outputs = await self.router.complete(role="verifier", system=system, prompt=prompt, n=1, temperature=0.1)
        return self._parse_score(outputs[0])

    def _parse_score(self, text: str) -> float:
        match = re.search(r"(-?\d+(?:\.\d+)?)", text)
        if not match:
            raise ValueError("No score found")
        score = float(match.group(1))
        return max(0.0, min(10.0, score))

    def _heuristic_score(self, hint: str) -> float:
        score = 5.0
        if "?" in hint:
            score += 2.0
        if len(hint) < 40:
            score -= 1.0
        if "solution" in hint.lower() or "fix" in hint.lower():
            score -= 2.0
        return max(0.0, min(10.0, score))
