# tests/test_graph_constructor.py
from __future__ import annotations

import json
import unittest

from backend.core.graph_constructor import GraphConstructor
from backend.core.misconception_graph import MisconceptionGraph


class FakeRouter:
    def __init__(self, responses: list[str]) -> None:
        self.responses = responses
        self.calls: list[dict] = []

    async def complete(self, role: str, system: str, prompt: str, n: int = 1, temperature: float = 0.7) -> list[str]:
        self.calls.append({"role": role, "system": system, "prompt": prompt, "n": n, "temperature": temperature})
        return [self.responses.pop(0)]


SAMPLE_PROBLEM = {
    "id": "p1",
    "statement": "Sum a list of integers.",
    "buggy_code": "def s(v):\n    t=0\n    for i in range(len(v)+1): t+=v[i]\n    return t",
    "starter_code": "def s(v):\n    t=0\n    for i in range(len(v)): t+=v[i]\n    return t",
    "bug_desc": "Off-by-one error: loop iterates one too many times, accessing out-of-range index.",
    "bug_fixes": "Change range(len(v)+1) to range(len(v)).",
}


class GraphConstructorTests(unittest.IsolatedAsyncioTestCase):
    async def test_builds_graph_from_problem(self) -> None:
        response = json.dumps({
            "nodes": [
                {"id": "M1", "name": "Off-by-one", "description": "Loop runs one extra time.",
                 "concept": "loop_boundary", "type": "conceptual"},
            ],
            "edges": [],
        })
        router = FakeRouter(responses=[response])
        gc = GraphConstructor(router=router)

        graph = await gc.build(SAMPLE_PROBLEM)

        self.assertIsInstance(graph, MisconceptionGraph)
        self.assertEqual(len(graph.nodes), 1)
        self.assertEqual(graph.nodes[0].id, "M1")
        self.assertEqual(graph.nodes[0].concept, "loop_boundary")
        self.assertEqual(router.calls[0]["role"], "planner")
        self.assertEqual(router.calls[0]["temperature"], 0.2)

    async def test_strips_cycles(self) -> None:
        response = json.dumps({
            "nodes": [
                {"id": "A", "name": "A", "description": "", "concept": "c", "type": "conceptual"},
                {"id": "B", "name": "B", "description": "", "concept": "c", "type": "conceptual"},
            ],
            "edges": [
                {"source": "A", "target": "B", "type": "prerequisite"},
                {"source": "B", "target": "A", "type": "prerequisite"},
            ],
        })
        router = FakeRouter(responses=[response])
        gc = GraphConstructor(router=router)
        graph = await gc.build(SAMPLE_PROBLEM)
        # At least one cycle edge must be removed
        self.assertLess(len(graph.edges), 2)

    async def test_filters_orphan_edges(self) -> None:
        response = json.dumps({
            "nodes": [{"id": "A", "name": "A", "description": "", "concept": "c", "type": "conceptual"}],
            "edges": [{"source": "A", "target": "Z", "type": "prerequisite"}],
        })
        router = FakeRouter(responses=[response])
        gc = GraphConstructor(router=router)
        graph = await gc.build(SAMPLE_PROBLEM)
        self.assertEqual(graph.edges, [])

    async def test_falls_back_to_single_node_on_invalid_json(self) -> None:
        router = FakeRouter(responses=["this is not json at all"])
        gc = GraphConstructor(router=router)
        graph = await gc.build(SAMPLE_PROBLEM)
        # Fallback: 1 node summarising bug_desc
        self.assertEqual(len(graph.nodes), 1)
        self.assertEqual(graph.edges, [])

    async def test_caps_node_count(self) -> None:
        nodes = [
            {"id": f"M{i}", "name": f"n{i}", "description": "", "concept": "c", "type": "conceptual"}
            for i in range(10)
        ]
        response = json.dumps({"nodes": nodes, "edges": []})
        router = FakeRouter(responses=[response])
        gc = GraphConstructor(router=router)
        graph = await gc.build(SAMPLE_PROBLEM)
        self.assertLessEqual(len(graph.nodes), 5)
