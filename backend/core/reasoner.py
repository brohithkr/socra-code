from __future__ import annotations

from typing import List, Protocol

from ..models.router import LLMRouter


class ChatTurn(Protocol):
    role: str
    content: str


class Reasoner:
    def __init__(self, router: LLMRouter) -> None:
        self.router = router

    async def summarize(
        self,
        code: str,
        output: str | None,
        user_message: str | None = None,
        chat_history: List[ChatTurn] | None = None,
    ) -> str:
        prompt = self._build_prompt(code, output, user_message, chat_history or [])
        system = "You are a code reasoning assistant. Return a concise bug diagnosis summary." 
        outputs = await self.router.complete(role="reasoner", system=system, prompt=prompt, n=1, temperature=0.3)
        return outputs[0]

    def _build_prompt(
        self,
        code: str,
        output: str | None,
        user_message: str | None = None,
        chat_history: List[ChatTurn] | None = None,
    ) -> str:
        output_block = output or "(no runtime output)"
        chat_block = self._format_chat(chat_history or [])
        student_message = user_message or "(no current student message)"
        return (
            "Analyze the buggy code, output, and student's latest doubt.\n"
            f"Output: {output_block}\n"
            f"Chat history:\n{chat_block}\n"
            f"Latest student message: {student_message}\n"
            "Code:\n"
            f"{code}\n"
            "Return a short diagnosis (2-4 sentences)."
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
