# tests/test_misconception_graph.py
from __future__ import annotations

import unittest

from backend.core.misconception_graph import (
    MisconceptionEdge,
    MisconceptionGraph,
    MisconceptionNode,
)


class MisconceptionGraphTests(unittest.TestCase):
    def test_node_lookup(self) -> None:
        n1 = MisconceptionNode(id="M1", name="Off-by-one", description="...", concept="loop_boundary", type="conceptual")
        graph = MisconceptionGraph(nodes=[n1], edges=[])
        self.assertIs(graph.node("M1"), n1)
        self.assertIsNone(graph.node("missing"))

    def test_prerequisites(self) -> None:
        n1 = MisconceptionNode(id="M1", name="A", description="", concept="x", type="conceptual")
        n2 = MisconceptionNode(id="M2", name="B", description="", concept="y", type="conceptual")
        e = MisconceptionEdge(source="M1", target="M2", type="prerequisite")
        graph = MisconceptionGraph(nodes=[n1, n2], edges=[e])
        self.assertEqual(graph.prerequisites_of("M2"), {"M1"})
        self.assertEqual(graph.prerequisites_of("M1"), set())

    def test_to_dict_round_trip(self) -> None:
        n1 = MisconceptionNode(id="M1", name="A", description="d", concept="c", type="conceptual")
        graph = MisconceptionGraph(nodes=[n1], edges=[])
        d = graph.to_dict()
        rebuilt = MisconceptionGraph.from_dict(d)
        self.assertEqual(rebuilt.nodes[0].id, "M1")
        self.assertEqual(len(rebuilt.edges), 0)
