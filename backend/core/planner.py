from __future__ import annotations

import json
from dataclasses import dataclass
from typing import List, Protocol

from ..models.router import LLMRouter


class ChatTurn(Protocol):
    role: str
    content: str


@dataclass
class Plan:
    bug_class: str
    hint_level: int
    strategy: str
    target_concept: str


class Planner:
    def __init__(self, router: LLMRouter) -> None:
        self.router = router

    async def plan(
        self,
        code: str,
        output: str | None,
        history: List[str],
        knowledge_state: dict,
        user_message: str | None = None,
        chat_history: List[ChatTurn] | None = None,
    ) -> Plan:
        prompt = self._build_prompt(code, output, history, knowledge_state, user_message, chat_history or [])
        system = "You are a tutoring planner that outputs JSON only."
        try:
            outputs = await self.router.complete(role="planner", system=system, prompt=prompt, n=1, temperature=0.2)
            plan_json = self._parse_json(outputs[0])
            return Plan(
                bug_class=plan_json.get("bug_class", "logic"),
                hint_level=int(plan_json.get("hint_level", max(1, len(history) + 1))),
                strategy=plan_json.get("strategy", "question"),
                target_concept=plan_json.get("target_concept", "logic"),
            )
        except Exception:
            return self._fallback_plan(code, output, history)

    def _build_prompt(
        self,
        code: str,
        output: str | None,
        history: List[str],
        knowledge_state: dict,
        user_message: str | None = None,
        chat_history: List[ChatTurn] | None = None,
    ) -> str:
        output_block = output or "(no runtime output)"
        chat_block = self._format_chat(chat_history or [])
        student_message = user_message or "(no current student message)"
        return (
            "Analyze the student's code, output, and latest doubt.\n"
            "Return JSON with keys: bug_class, hint_level, strategy, target_concept.\n"
            f"Output: {output_block}\n"
            f"History length: {len(history)}\n"
            f"Prior hint history: {json.dumps(history)}\n"
            f"Chat history:\n{chat_block}\n"
            f"Latest student message: {student_message}\n"
            f"Knowledge state: {json.dumps(knowledge_state)}\n"
            "Code:\n"
            f"{code}\n"
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

    def _parse_json(self, text: str) -> dict:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1:
            raise ValueError("No JSON found")
        return json.loads(text[start : end + 1])

    def _fallback_plan(self, code: str, output: str | None, history: List[str]) -> Plan:
        bug_class = "logic"
        target = "flow"
        if output:
            lowered = output.lower()
            if "index" in lowered or "out of range" in lowered:
                bug_class = "off-by-one"
                target = "loop boundary"
            elif "type" in lowered:
                bug_class = "type"
                target = "type handling"
            elif "null" in lowered or "none" in lowered:
                bug_class = "null"
                target = "null safety"
        hint_level = min(3, 1 + len(history))
        strategy = "question" if hint_level <= 2 else "nudge"
        return Plan(
            bug_class=bug_class,
            hint_level=hint_level,
            strategy=strategy,
            target_concept=target,
        )
