from __future__ import annotations

from typing import List, Protocol

from .planner import Plan
from ..models.router import LLMRouter


class ChatTurn(Protocol):
    role: str
    content: str


class Generator:
    def __init__(self, router: LLMRouter) -> None:
        self.router = router

    async def generate(
        self,
        plan: Plan,
        code: str,
        output: str | None,
        reasoning_summary: str,
        user_message: str | None = None,
        chat_history: List[ChatTurn] | None = None,
        n: int = 5,
    ) -> List[str]:
        prompt = self._build_prompt(plan, code, output, reasoning_summary, user_message, chat_history or [])
        system = "You are a Socratic coding tutor. Ask one guiding question."
        return await self.router.complete(role="tutor", system=system, prompt=prompt, n=n, temperature=0.7)

    def _build_prompt(
        self,
        plan: Plan,
        code: str,
        output: str | None,
        reasoning_summary: str,
        user_message: str | None = None,
        chat_history: List[ChatTurn] | None = None,
    ) -> str:
        output_block = output or "(no runtime output)"
        chat_block = self._format_chat(chat_history or [])
        student_message = user_message or "(no current student message)"
        return (
            "You are a Socratic tutor. Use questioning strategies like:\n"
            "- Situational probing\n"
            "- ZPD guidance\n"
            "- Metacognitive reflection\n"
            "Rules: Ask ONE question that responds to the student's doubt. No direct fixes. No code dumps.\n\n"
            f"Plan: bug_class={plan.bug_class}, target={plan.target_concept}, strategy={plan.strategy}.\n"
            f"Output: {output_block}\n"
            f"Reasoning summary: {reasoning_summary}\n"
            f"Chat history:\n{chat_block}\n"
            f"Latest student message: {student_message}\n"
            "Code:\n"
            f"{code}\n"
            "Return only the question."
        )

    def _format_chat(self, chat_history: List[ChatTurn]) -> str:
        if not chat_history:
            return "(no chat history)"
        lines = []
        for turn in chat_history[-8:]:
            role = turn.get("role", "student") if isinstance(turn, dict) else turn.role
            content = turn.get("content", "") if isinstance(turn, dict) else turn.content
            lines.append(f"{role}: {content}")
        return "\n".join(lines)
