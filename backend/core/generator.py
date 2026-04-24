from __future__ import annotations

from typing import List

from .planner import Plan
from ..models.router import LLMRouter


class Generator:
    def __init__(self, router: LLMRouter) -> None:
        self.router = router

    async def generate(
        self,
        plan: Plan,
        code: str,
        output: str | None,
        reasoning_summary: str,
        n: int = 5,
    ) -> List[str]:
        prompt = self._build_prompt(plan, code, output, reasoning_summary)
        system = "You are a Socratic coding tutor. Ask one guiding question."
        return await self.router.complete(role="tutor", system=system, prompt=prompt, n=n, temperature=0.7)

    def _build_prompt(
        self,
        plan: Plan,
        code: str,
        output: str | None,
        reasoning_summary: str,
    ) -> str:
        output_block = output or "(no runtime output)"
        return (
            "You are a Socratic tutor. Use questioning strategies like:\n"
            "- Situational probing\n"
            "- ZPD guidance\n"
            "- Metacognitive reflection\n"
            "Rules: Ask ONE question. No direct fixes. No code dumps.\n\n"
            f"Plan: bug_class={plan.bug_class}, target={plan.target_concept}, strategy={plan.strategy}.\n"
            f"Output: {output_block}\n"
            f"Reasoning summary: {reasoning_summary}\n"
            "Code:\n"
            f"{code}\n"
            "Return only the question."
        )
