# backend/core/traversal_engine.py
from __future__ import annotations

from typing import Optional, Set

from .misconception_graph import MisconceptionGraph


class TraversalEngine:
    """Picks the next misconception to address based on graph topology and resolved set.

    Pure logic — no LLM calls. Deterministic: walks nodes in declaration order
    and returns the first unresolved node whose prerequisites are all resolved.
    """

    def pick_next(
        self,
        graph: MisconceptionGraph,
        resolved: Set[str],
    ) -> Optional[str]:
        for node in graph.nodes:
            if node.id in resolved:
                continue
            prereqs = graph.prerequisites_of(node.id)
            if prereqs.issubset(resolved):
                return node.id
        return None
