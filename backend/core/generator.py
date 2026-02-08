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
        error: str | None,
        rag_snippets: List[str],
        reasoning_summary: str,
        n: int = 5,
    ) -> List[str]:
        prompt = self._build_prompt(plan, code, error, rag_snippets, reasoning_summary)
        system = "You are a Socratic coding tutor. Ask one guiding question."
        return await self.router.complete(role="tutor", system=system, prompt=prompt, n=n, temperature=0.7)

    def _build_prompt(
        self,
        plan: Plan,
        code: str,
        error: str | None,
        rag_snippets: List[str],
        reasoning_summary: str,
    ) -> str:
        rag_block = "\n\n".join(rag_snippets) if rag_snippets else "(none)"
        error_block = error or "(no runtime error)"
        return (
            "You are a Socratic tutor. Use questioning strategies like:\n"
            "- Situational probing\n"
            "- ZPD guidance\n"
            "- Metacognitive reflection\n"
            "Rules: Ask ONE question. No direct fixes. No code dumps.\n\n"
            f"Plan: bug_class={plan.bug_class}, target={plan.target_concept}, strategy={plan.strategy}.\n"
            f"Error: {error_block}\n"
            f"Reasoning summary: {reasoning_summary}\n"
            "Code:\n"
            f"{code}\n"
            "RAG snippets (internal context):\n"
            f"{rag_block}\n"
            "Return only the question."
        )
