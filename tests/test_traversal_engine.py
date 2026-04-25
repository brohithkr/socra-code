# tests/test_traversal_engine.py
from __future__ import annotations

import unittest

from backend.core.misconception_graph import (
    MisconceptionEdge,
    MisconceptionGraph,
    MisconceptionNode,
)
from backend.core.traversal_engine import TraversalEngine


def _node(id: str, concept: str = "c") -> MisconceptionNode:
    return MisconceptionNode(id=id, name=id, description="", concept=concept, type="conceptual")


class TraversalEngineTests(unittest.TestCase):
    def test_pick_first_returns_node_with_no_prerequisites(self) -> None:
        graph = MisconceptionGraph(
            nodes=[_node("A"), _node("B")],
            edges=[MisconceptionEdge(source="A", target="B", type="prerequisite")],
        )
        engine = TraversalEngine()
        self.assertEqual(engine.pick_next(graph, resolved=set()), "A")

    def test_pick_next_skips_already_resolved(self) -> None:
        graph = MisconceptionGraph(
            nodes=[_node("A"), _node("B")],
            edges=[MisconceptionEdge(source="A", target="B", type="prerequisite")],
        )
        engine = TraversalEngine()
        self.assertEqual(engine.pick_next(graph, resolved={"A"}), "B")

    def test_returns_none_when_all_resolved(self) -> None:
        graph = MisconceptionGraph(nodes=[_node("A")], edges=[])
        engine = TraversalEngine()
        self.assertIsNone(engine.pick_next(graph, resolved={"A"}))

    def test_blocks_node_with_unresolved_prerequisite(self) -> None:
        graph = MisconceptionGraph(
            nodes=[_node("A"), _node("B"), _node("C")],
            edges=[
                MisconceptionEdge(source="A", target="C", type="prerequisite"),
                MisconceptionEdge(source="B", target="C", type="prerequisite"),
            ],
        )
        engine = TraversalEngine()
        # Resolve only A — C still blocked by B
        self.assertEqual(engine.pick_next(graph, resolved={"A"}), "B")

    def test_related_edges_do_not_block(self) -> None:
        graph = MisconceptionGraph(
            nodes=[_node("A"), _node("B")],
            edges=[MisconceptionEdge(source="A", target="B", type="related")],
        )
        engine = TraversalEngine()
        # Even though no prerequisites, picks first available — A by node order
        self.assertEqual(engine.pick_next(graph, resolved=set()), "A")

    def test_deterministic_ordering(self) -> None:
        graph = MisconceptionGraph(nodes=[_node("X"), _node("Y"), _node("Z")], edges=[])
        engine = TraversalEngine()
        # No prereqs — picks first by node list order
        self.assertEqual(engine.pick_next(graph, resolved=set()), "X")
        self.assertEqual(engine.pick_next(graph, resolved={"X"}), "Y")
