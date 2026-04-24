from __future__ import annotations

import unittest

from backend.core.pipeline import HintPipeline
from backend.core.planner import Plan


class FakePlanner:
    def __init__(self) -> None:
        self.calls = []

    async def plan(self, code: str, error: str | None, history: list[str], knowledge_state: dict) -> Plan:
        self.calls.append(
            {
                "code": code,
                "error": error,
                "history": list(history),
                "knowledge_state": dict(knowledge_state),
            }
        )
        return Plan(
            bug_class="off-by-one",
            hint_level=1,
            strategy="question",
            target_concept="loop boundary",
        )


class FakeReasoner:
    def __init__(self) -> None:
        self.calls = []

    async def summarize(self, code: str, error: str | None) -> str:
        self.calls.append({"code": code, "error": error})
        return "The loop likely runs one step too far."


class FakeGenerator:
    def __init__(self) -> None:
        self.calls = []

    async def generate(
        self,
        plan: Plan,
        code: str,
        error: str | None,
        reasoning_summary: str,
        n: int = 5,
    ) -> list[str]:
        self.calls.append(
            {
                "plan": plan,
                "code": code,
                "error": error,
                "reasoning_summary": reasoning_summary,
                "n": n,
            }
        )
        return [
            "What happens when the loop reaches the final index?",
            "Can you trace the last iteration by hand?",
        ]


class FakeVerifier:
    def __init__(self) -> None:
        self.calls = []

    async def score(self, candidates: list[str], context: str, use_llm: bool = True) -> list[tuple[str, float]]:
        self.calls.append(
            {
                "candidates": list(candidates),
                "context": context,
                "use_llm": use_llm,
            }
        )
        return [(candidates[0], 7.2), (candidates[1], 6.1)]


class FakeTracer:
    def __init__(self) -> None:
        self.snapshots = []
        self.hints = []

    async def snapshot(self, session_id: str) -> dict:
        self.snapshots.append(session_id)
        return {"loop boundary": 0.4}

    async def note_hint(self, session_id: str, concept: str) -> None:
        self.hints.append((session_id, concept))


class HintPipelineTests(unittest.IsolatedAsyncioTestCase):
    async def test_run_generates_hint_without_retrieval_context(self) -> None:
        planner = FakePlanner()
        reasoner = FakeReasoner()
        generator = FakeGenerator()
        verifier = FakeVerifier()
        tracer = FakeTracer()
        pipeline = HintPipeline(planner, reasoner, generator, verifier, tracer)

        hint, plan, score = await pipeline.run(
            code="for i in range(len(values) + 1): pass",
            error="IndexError: list index out of range",
            history=["Can you help?"],
            session_id="practice",
            candidate_count=2,
            verifier_use_llm=False,
        )

        self.assertEqual(hint, "What happens when the loop reaches the final index?")
        self.assertEqual(score, 7.2)
        self.assertEqual(plan.target_concept, "loop boundary")
        self.assertEqual(tracer.snapshots, ["practice"])
        self.assertEqual(tracer.hints, [("practice", "loop boundary")])
        self.assertEqual(planner.calls[0]["knowledge_state"], {"loop boundary": 0.4})
        self.assertEqual(reasoner.calls, [{"code": "for i in range(len(values) + 1): pass", "error": "IndexError: list index out of range"}])
        self.assertEqual(generator.calls[0]["reasoning_summary"], "The loop likely runs one step too far.")
        self.assertEqual(generator.calls[0]["n"], 2)
        self.assertNotIn("RAG", verifier.calls[0]["context"])

