from __future__ import annotations

import unittest

from backend.core.misconception_graph import (
    MisconceptionEdge,
    MisconceptionGraph,
    MisconceptionNode,
)
from backend.core.response_evaluator import EvaluationResult
from backend.core.socratic_pipeline import SocraticPipeline, SocraticResult
from backend.core.student_model import StudentModelStore


def _node(id: str) -> MisconceptionNode:
    return MisconceptionNode(id=id, name=id, description="", concept=id.lower(), type="conceptual")


class FakeGraphConstructor:
    def __init__(self, graph: MisconceptionGraph) -> None:
        self.graph = graph
        self.calls = 0

    async def build(self, problem: dict) -> MisconceptionGraph:
        self.calls += 1
        return self.graph


class FakeQuestionGenerator:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    async def generate(self, node, hint_level, code, output, chat_history) -> str:
        self.calls.append({
            "node_id": node.id,
            "hint_level": hint_level,
            "code": code,
        })
        return f"Q for {node.id} at level {hint_level}"


class FakeEvaluator:
    def __init__(self, results: list[EvaluationResult]) -> None:
        self.results = results
        self.calls = 0

    async def evaluate(self, node, previous_question, student_response) -> EvaluationResult:
        result = self.results[self.calls]
        self.calls += 1
        return result


SAMPLE_PROBLEM = {
    "id": "p1",
    "statement": "...",
    "buggy_code": "...",
    "starter_code": "...",
    "bug_desc": "off-by-one",
    "bug_fixes": "fix range",
}


class SocraticPipelineTests(unittest.IsolatedAsyncioTestCase):
    async def test_first_turn_builds_graph_and_returns_first_question(self) -> None:
        graph = MisconceptionGraph(
            nodes=[_node("M1"), _node("M2")],
            edges=[MisconceptionEdge(source="M1", target="M2", type="prerequisite")],
        )
        store = StudentModelStore()
        pipeline = SocraticPipeline(
            graph_constructor=FakeGraphConstructor(graph),
            traversal=__import__("backend.core.traversal_engine", fromlist=["TraversalEngine"]).TraversalEngine(),
            question_generator=FakeQuestionGenerator(),
            response_evaluator=FakeEvaluator([]),
            student_store=store,
        )

        result = await pipeline.run(
            session_id="s1",
            problem=SAMPLE_PROBLEM,
            code="x",
            output=None,
            user_message=None,
            chat_history=[],
        )

        self.assertIsInstance(result, SocraticResult)
        self.assertEqual(result.hint, "Q for M1 at level 0")
        self.assertEqual(result.progress["resolved"], 0)
        self.assertEqual(result.progress["total"], 2)
        self.assertEqual(result.progress["level"], 0)

        # State persisted
        student = await store.get_or_create("s1")
        self.assertEqual(student.current_node_id, "M1")
        self.assertEqual(student.hint_level, 0)
        self.assertEqual(student.last_question, "Q for M1 at level 0")

    async def test_strong_response_advances_to_next_node(self) -> None:
        graph = MisconceptionGraph(
            nodes=[_node("M1"), _node("M2")],
            edges=[MisconceptionEdge(source="M1", target="M2", type="prerequisite")],
        )
        store = StudentModelStore()
        evaluator = FakeEvaluator([
            EvaluationResult(understanding="strong", delta=0.35, rationale="ok"),
        ])
        traversal = __import__("backend.core.traversal_engine", fromlist=["TraversalEngine"]).TraversalEngine()
        pipeline = SocraticPipeline(
            graph_constructor=FakeGraphConstructor(graph),
            traversal=traversal,
            question_generator=FakeQuestionGenerator(),
            response_evaluator=evaluator,
            student_store=store,
        )

        # Turn 1
        await pipeline.run(session_id="s1", problem=SAMPLE_PROBLEM, code="x",
                           output=None, user_message=None, chat_history=[])
        # Turn 2 — student answers correctly
        result = await pipeline.run(
            session_id="s1",
            problem=SAMPLE_PROBLEM,
            code="x",
            output=None,
            user_message="I see the bug.",
            chat_history=[],
        )

        self.assertEqual(result.hint, "Q for M2 at level 0")
        self.assertEqual(result.progress["resolved"], 1)
        student = await store.get_or_create("s1")
        self.assertIn("M1", student.resolved_node_ids)
        self.assertEqual(student.current_node_id, "M2")
        self.assertEqual(student.hint_level, 0)

    async def test_partial_response_escalates_hint_level(self) -> None:
        graph = MisconceptionGraph(nodes=[_node("M1")], edges=[])
        store = StudentModelStore()
        evaluator = FakeEvaluator([
            EvaluationResult(understanding="partial", delta=0.15, rationale=""),
        ])
        traversal = __import__("backend.core.traversal_engine", fromlist=["TraversalEngine"]).TraversalEngine()
        pipeline = SocraticPipeline(
            graph_constructor=FakeGraphConstructor(graph),
            traversal=traversal,
            question_generator=FakeQuestionGenerator(),
            response_evaluator=evaluator,
            student_store=store,
        )

        await pipeline.run(session_id="s1", problem=SAMPLE_PROBLEM, code="x",
                           output=None, user_message=None, chat_history=[])
        result = await pipeline.run(session_id="s1", problem=SAMPLE_PROBLEM, code="x",
                                    output=None, user_message="not sure", chat_history=[])

        self.assertEqual(result.hint, "Q for M1 at level 1")
        student = await store.get_or_create("s1")
        self.assertEqual(student.hint_level, 1)
        self.assertNotIn("M1", student.resolved_node_ids)

    async def test_completion_when_all_resolved(self) -> None:
        graph = MisconceptionGraph(nodes=[_node("M1")], edges=[])
        store = StudentModelStore()
        evaluator = FakeEvaluator([
            EvaluationResult(understanding="strong", delta=0.35, rationale="ok"),
        ])
        traversal = __import__("backend.core.traversal_engine", fromlist=["TraversalEngine"]).TraversalEngine()
        pipeline = SocraticPipeline(
            graph_constructor=FakeGraphConstructor(graph),
            traversal=traversal,
            question_generator=FakeQuestionGenerator(),
            response_evaluator=evaluator,
            student_store=store,
        )

        await pipeline.run(session_id="s1", problem=SAMPLE_PROBLEM, code="x",
                           output=None, user_message=None, chat_history=[])
        result = await pipeline.run(session_id="s1", problem=SAMPLE_PROBLEM, code="x",
                                    output=None, user_message="got it", chat_history=[])

        self.assertEqual(result.progress["resolved"], 1)
        self.assertEqual(result.progress["total"], 1)
        self.assertIn("worked through", result.hint.lower())

    async def test_problem_change_resets_state(self) -> None:
        graph_a = MisconceptionGraph(nodes=[_node("A1")], edges=[])
        graph_b = MisconceptionGraph(nodes=[_node("B1")], edges=[])
        store = StudentModelStore()
        traversal = __import__("backend.core.traversal_engine", fromlist=["TraversalEngine"]).TraversalEngine()

        # Construct one pipeline that returns different graphs depending on problem
        class SwitchingConstructor:
            async def build(self, problem):
                return graph_a if problem["id"] == "p1" else graph_b

        pipeline = SocraticPipeline(
            graph_constructor=SwitchingConstructor(),
            traversal=traversal,
            question_generator=FakeQuestionGenerator(),
            response_evaluator=FakeEvaluator([]),
            student_store=store,
        )

        await pipeline.run(session_id="s1", problem={"id": "p1", "bug_desc": "...", "bug_fixes": "..."},
                           code="x", output=None, user_message=None, chat_history=[])
        student = await store.get_or_create("s1")
        self.assertEqual(student.current_node_id, "A1")

        # Switch to a different problem
        await pipeline.run(session_id="s1", problem={"id": "p2", "bug_desc": "...", "bug_fixes": "..."},
                           code="y", output=None, user_message=None, chat_history=[])
        student = await store.get_or_create("s1")
        self.assertEqual(student.problem_id, "p2")
        self.assertEqual(student.current_node_id, "B1")
        self.assertEqual(student.resolved_node_ids, set())
        self.assertEqual(student.hint_level, 0)
