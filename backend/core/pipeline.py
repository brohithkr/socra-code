from __future__ import annotations

from typing import List, Protocol, Tuple

from .planner import Planner, Plan
from .generator import Generator
from .verifier import Verifier
from .reasoner import Reasoner
from .knowledge_tracer import KnowledgeTracer


class ChatTurn(Protocol):
    role: str
    content: str


class HintPipeline:
    def __init__(
        self,
        planner: Planner,
        reasoner: Reasoner,
        generator: Generator,
        verifier: Verifier,
        tracer: KnowledgeTracer,
    ) -> None:
        self.planner = planner
        self.reasoner = reasoner
        self.generator = generator
        self.verifier = verifier
        self.tracer = tracer

    async def run(
        self,
        code: str,
        output: str | None,
        history: List[str],
        session_id: str,
        user_message: str | None = None,
        chat_history: List[ChatTurn] | None = None,
        candidate_count: int = 5,
        verifier_use_llm: bool = True,
    ) -> Tuple[str, Plan, float]:
        chat_history = chat_history or []
        knowledge_state = await self.tracer.snapshot(session_id)
        plan = await self.planner.plan(
            code=code,
            output=output,
            history=history,
            knowledge_state=knowledge_state,
            user_message=user_message,
            chat_history=chat_history,
        )
        reasoning = await self.reasoner.summarize(
            code=code,
            output=output,
            user_message=user_message,
            chat_history=chat_history,
        )
        candidates = await self.generator.generate(
            plan=plan,
            code=code,
            output=output,
            reasoning_summary=reasoning,
            user_message=user_message,
            chat_history=chat_history,
            n=max(1, candidate_count),
        )
        context = (
            f"Plan: {plan}. Output: {output or ''}. "
            f"Student message: {user_message or ''}. Reasoning: {reasoning}"
        )
        scored = await self.verifier.score(candidates, context=context, use_llm=verifier_use_llm)
        scored.sort(key=lambda x: x[1], reverse=True)
        best_hint, best_score = scored[0]
        await self.tracer.note_hint(session_id, plan.target_concept)
        return best_hint, plan, best_score
