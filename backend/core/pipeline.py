from __future__ import annotations

from typing import List, Tuple

from .planner import Planner, Plan
from .rag import RAGEngine
from .generator import Generator
from .verifier import Verifier
from .reasoner import Reasoner
from .knowledge_tracer import KnowledgeTracer


class HintPipeline:
    def __init__(
        self,
        planner: Planner,
        rag: RAGEngine,
        reasoner: Reasoner,
        generator: Generator,
        verifier: Verifier,
        tracer: KnowledgeTracer,
        rag_top_k: int,
    ) -> None:
        self.planner = planner
        self.rag = rag
        self.reasoner = reasoner
        self.generator = generator
        self.verifier = verifier
        self.tracer = tracer
        self.rag_top_k = rag_top_k

    async def run(
        self,
        code: str,
        error: str | None,
        history: List[str],
        session_id: str,
        candidate_count: int = 5,
        verifier_use_llm: bool = True,
    ) -> Tuple[str, Plan, float]:
        knowledge_state = await self.tracer.snapshot(session_id)
        plan = await self.planner.plan(code=code, error=error, history=history, knowledge_state=knowledge_state)
        rag_snippets = self.rag.search(f"{code}\n{error or ''}", top_k=self.rag_top_k)
        reasoning = await self.reasoner.summarize(code=code, error=error, rag_snippets=rag_snippets)
        candidates = await self.generator.generate(
            plan=plan,
            code=code,
            error=error,
            rag_snippets=rag_snippets,
            reasoning_summary=reasoning,
            n=max(1, candidate_count),
        )
        context = f"Plan: {plan}. Error: {error or ''}. Reasoning: {reasoning}"
        scored = await self.verifier.score(candidates, context=context, use_llm=verifier_use_llm)
        scored.sort(key=lambda x: x[1], reverse=True)
        best_hint, best_score = scored[0]
        await self.tracer.note_hint(session_id, plan.target_concept)
        return best_hint, plan, best_score
