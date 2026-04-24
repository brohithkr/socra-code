from __future__ import annotations

import unittest

from backend.core.pipeline import HintPipeline
from backend.core.planner import Plan


class FakePlanner:
    def __init__(self) -> None:
        self.calls = []

    async def plan(
        self,
        code: str,
        output: str | None,
        history: list[str],
        knowledge_state: dict,
        user_message: str | None = None,
        chat_history: list | None = None,
    ) -> Plan:
        self.calls.append(
            {
                "code": code,
                "output": output,
                "history": list(history),
                "knowledge_state": dict(knowledge_state),
                "user_message": user_message,
                "chat_history": list(chat_history or []),
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

    async def summarize(
        self,
        code: str,
        output: str | None,
        user_message: str | None = None,
        chat_history: list | None = None,
    ) -> str:
        self.calls.append(
            {
                "code": code,
                "output": output,
                "user_message": user_message,
                "chat_history": list(chat_history or []),
            }
        )
        return "The loop likely runs one step too far."


class FakeGenerator:
    def __init__(self) -> None:
        self.calls = []

    async def generate(
        self,
        plan: Plan,
        code: str,
        output: str | None,
        reasoning_summary: str,
        user_message: str | None = None,
        chat_history: list | None = None,
        n: int = 5,
    ) -> list[str]:
        self.calls.append(
            {
                "plan": plan,
                "code": code,
                "output": output,
                "reasoning_summary": reasoning_summary,
                "user_message": user_message,
                "chat_history": list(chat_history or []),
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


class FakeStudentStore:
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
        student_store = FakeStudentStore()
        pipeline = HintPipeline(planner, reasoner, generator, verifier, student_store)

        hint, plan, score = await pipeline.run(
            code="for i in range(len(values) + 1): pass",
            output="IndexError: list index out of range",
            history=["Can you help?"],
            user_message="Why is the last item crashing?",
            chat_history=[{"role": "student", "content": "I think the loop is fine."}],
            session_id="practice",
            candidate_count=2,
            verifier_use_llm=False,
        )

        self.assertEqual(hint, "What happens when the loop reaches the final index?")
        self.assertEqual(score, 7.2)
        self.assertEqual(plan.target_concept, "loop boundary")
        self.assertEqual(student_store.snapshots, ["practice"])
        self.assertEqual(student_store.hints, [("practice", "loop boundary")])
        self.assertEqual(planner.calls[0]["knowledge_state"], {"loop boundary": 0.4})
        self.assertEqual(reasoner.calls[0]["output"], "IndexError: list index out of range")
        self.assertEqual(reasoner.calls[0]["user_message"], "Why is the last item crashing?")
        self.assertEqual(generator.calls[0]["chat_history"], [{"role": "student", "content": "I think the loop is fine."}])
        self.assertEqual(generator.calls[0]["reasoning_summary"], "The loop likely runs one step too far.")
        self.assertEqual(generator.calls[0]["n"], 2)
        self.assertNotIn("RAG", verifier.calls[0]["context"])
