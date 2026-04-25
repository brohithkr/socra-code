# tests/test_response_evaluator.py
from __future__ import annotations

import json
import unittest

from backend.core.misconception_graph import MisconceptionNode
from backend.core.response_evaluator import (
    EvaluationResult,
    ResponseEvaluator,
    UNDERSTANDING_DELTA,
)


class FakeRouter:
    def __init__(self, response: str) -> None:
        self.response = response
        self.calls: list[dict] = []

    async def complete(self, role: str, system: str, prompt: str, n: int = 1, temperature: float = 0.7) -> list[str]:
        self.calls.append({"role": role, "system": system, "prompt": prompt, "n": n, "temperature": temperature})
        return [self.response]


NODE = MisconceptionNode(
    id="M1",
    name="Off-by-one",
    description="Loop iterates one too many times.",
    concept="loop_boundary",
    type="conceptual",
)


class ResponseEvaluatorTests(unittest.IsolatedAsyncioTestCase):
    async def test_strong_understanding(self) -> None:
        router = FakeRouter(json.dumps({"understanding": "strong", "rationale": "ok"}))
        ev = ResponseEvaluator(router)
        result = await ev.evaluate(
            node=NODE,
            previous_question="What happens at the last index?",
            student_response="I see — len(x) is one past the last valid index.",
        )
        self.assertIsInstance(result, EvaluationResult)
        self.assertEqual(result.understanding, "strong")
        self.assertEqual(result.delta, UNDERSTANDING_DELTA["strong"])

    async def test_partial_understanding(self) -> None:
        router = FakeRouter(json.dumps({"understanding": "partial", "rationale": ""}))
        ev = ResponseEvaluator(router)
        result = await ev.evaluate(node=NODE, previous_question="q", student_response="r")
        self.assertEqual(result.understanding, "partial")
        self.assertEqual(result.delta, UNDERSTANDING_DELTA["partial"])

    async def test_none_understanding(self) -> None:
        router = FakeRouter(json.dumps({"understanding": "none", "rationale": ""}))
        ev = ResponseEvaluator(router)
        result = await ev.evaluate(node=NODE, previous_question="q", student_response="huh?")
        self.assertEqual(result.understanding, "none")
        self.assertEqual(result.delta, UNDERSTANDING_DELTA["none"])

    async def test_uses_verifier_role(self) -> None:
        router = FakeRouter(json.dumps({"understanding": "none", "rationale": ""}))
        ev = ResponseEvaluator(router)
        await ev.evaluate(node=NODE, previous_question="q", student_response="r")
        self.assertEqual(router.calls[0]["role"], "verifier")

    async def test_falls_back_to_none_on_invalid_json(self) -> None:
        router = FakeRouter("garbage not json")
        ev = ResponseEvaluator(router)
        result = await ev.evaluate(node=NODE, previous_question="q", student_response="r")
        self.assertEqual(result.understanding, "none")

    async def test_falls_back_to_none_on_unknown_label(self) -> None:
        router = FakeRouter(json.dumps({"understanding": "supreme", "rationale": ""}))
        ev = ResponseEvaluator(router)
        result = await ev.evaluate(node=NODE, previous_question="q", student_response="r")
        self.assertEqual(result.understanding, "none")
