# backend/core/question_generator.py
from __future__ import annotations

from typing import Dict, List, Optional, Protocol

from ..models.router import LLMRouter
from .misconception_graph import MisconceptionNode


class ChatTurn(Protocol):
    role: str
    content: str


# Per-level system prompts. Each is a complete instruction — no conditionals at
# call site. Different levels are distinct prompts so the LLM does not bleed
# behaviors across levels.
LEVEL_PROMPTS: Dict[int, str] = {
    0: (
        "You are a Socratic tutor. Ask ONE open-ended question that helps the "
        "student notice the relevant area of code. Do NOT name the bug. Do NOT "
        "point at a specific line. No code dumps. No fixes. Reply with the "
        "question only."
    ),
    1: (
        "You are a Socratic tutor. Ask ONE question that points the student to "
        "a specific part of their code (a line, variable, or expression). The "
        "question must make them examine that location, not give the answer. "
        "Do NOT explain the bug. Reply with the question only."
    ),
    2: (
        "You are a Socratic tutor. Help the student trace through their code at "
        "a specific input. Ask ONE question about what value or state results "
        "at the relevant point — let them realise the discrepancy. Do NOT state "
        "the discrepancy yourself. Reply with the question only."
    ),
    3: (
        "You are a Socratic tutor. Show a small, complete, working contrastive "
        "example (3-8 lines) that differs from the student's approach in the "
        "relevant way. Format the example in a fenced markdown code block. After "
        "the example, ask ONE question about why theirs differs. Do NOT state "
        "the answer."
    ),
    4: (
        "You are a Socratic tutor. The student is stuck. Name the misconception "
        "in 1 sentence. Briefly explain why it is wrong in 1 sentence. Then ask "
        "ONE question that has the student apply the corrected understanding. "
        "No code dump."
    ),
}


def _format_chat(chat_history: List[ChatTurn]) -> str:
    if not chat_history:
        return "(no chat history)"
    lines = []
    for turn in chat_history[-8:]:
        role = turn.get("role", "student") if isinstance(turn, dict) else turn.role
        content = turn.get("content", "") if isinstance(turn, dict) else turn.content
        lines.append(f"{role}: {content}")
    return "\n".join(lines)


def _build_user_prompt(
    node: MisconceptionNode,
    code: str,
    output: Optional[str],
    chat_history: List[ChatTurn],
) -> str:
    output_block = output or "(no runtime output)"
    chat_block = _format_chat(chat_history)
    return (
        f"Misconception to address:\n"
        f"  Name: {node.name}\n"
        f"  Description: {node.description}\n\n"
        f"Student's current code:\n{code}\n\n"
        f"Runtime output:\n{output_block}\n\n"
        f"Conversation so far:\n{chat_block}\n"
    )


class QuestionGenerator:
    def __init__(self, router: LLMRouter) -> None:
        self.router = router

    async def generate(
        self,
        node: MisconceptionNode,
        hint_level: int,
        code: str,
        output: Optional[str],
        chat_history: List[ChatTurn],
    ) -> str:
        level = max(0, min(4, hint_level))
        system = LEVEL_PROMPTS[level]
        prompt = _build_user_prompt(node, code, output, chat_history)
        outputs = await self.router.complete(
            role="tutor",
            system=system,
            prompt=prompt,
            n=1,
            temperature=0.7,
        )
        return outputs[0].strip()
