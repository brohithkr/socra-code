# backend/core/graph_constructor.py
from __future__ import annotations

from typing import Any, Dict, List, Set

from ..models.router import LLMRouter
from .misconception_graph import (
    MisconceptionEdge,
    MisconceptionGraph,
    MisconceptionNode,
)
from .utils import parse_json


MAX_NODES = 5


SYSTEM_PROMPT = "You are a tutoring planner that outputs JSON only. No prose."


def _build_prompt(problem: Dict[str, Any]) -> str:
    return (
        "A student is debugging this problem. Identify the misconceptions the student "
        "likely has, based ONLY on evidence in the bug description and code diff. "
        "DO NOT invent additional misconceptions. If only one misconception is clearly "
        "evidenced, return a SINGLE node and no edges.\n\n"
        f"Problem statement:\n{problem.get('statement', '')}\n\n"
        f"Bug description:\n{problem.get('bug_desc', '')}\n\n"
        f"Bug fix:\n{problem.get('bug_fixes', '')}\n\n"
        f"Buggy code:\n{problem.get('buggy_code', '')}\n\n"
        f"Correct code:\n{problem.get('starter_code', '')}\n\n"
        "Return JSON in this exact shape:\n"
        "{\n"
        '  "nodes": [\n'
        '    {"id": "M1", "name": "short name (<=6 words)", '
        '"description": "1 sentence about what student misunderstands", '
        '"concept": "snake_case_concept_tag", "type": "conceptual" or "syntactical"}\n'
        "  ],\n"
        '  "edges": [\n'
        '    {"source": "M1", "target": "M2", "type": "prerequisite" or "related"}\n'
        "  ]\n"
        "}\n\n"
        "Rules:\n"
        "- 1 to 5 nodes maximum.\n"
        "- Edge type 'prerequisite' = student must understand source before target.\n"
        "- Edge type 'related' = both reinforce each other (no ordering).\n"
        "- No cycles. No self-loops.\n"
        "- Use stable IDs M1, M2, M3, ...\n"
    )


class GraphConstructor:
    def __init__(self, router: LLMRouter) -> None:
        self.router = router

    async def build(self, problem: Dict[str, Any]) -> MisconceptionGraph:
        prompt = _build_prompt(problem)
        try:
            outputs = await self.router.complete(
                role="planner",
                system=SYSTEM_PROMPT,
                prompt=prompt,
                n=1,
                temperature=0.2,
            )
            parsed = parse_json(outputs[0])
            return self._validate(parsed)
        except (ValueError, KeyError, TypeError) as exc:
            # Known recoverable errors: bad JSON, missing fields, wrong types.
            # Re-raises any unexpected exception so it surfaces during testing.
            _ = exc
            return self._fallback(problem)

    def _validate(self, data: Dict[str, Any]) -> MisconceptionGraph:
        raw_nodes = data.get("nodes", [])[:MAX_NODES]
        valid_nodes: List[MisconceptionNode] = []
        for raw in raw_nodes:
            try:
                node_type = str(raw.get("type", "conceptual"))
                if node_type not in ("conceptual", "syntactical"):
                    node_type = "conceptual"
                valid_nodes.append(
                    MisconceptionNode(
                        id=str(raw["id"]),
                        name=str(raw.get("name", raw["id"])),
                        description=str(raw.get("description", "")),
                        concept=str(raw.get("concept", "general")),
                        type=node_type,  # type: ignore[arg-type]
                    )
                )
            except (KeyError, TypeError):
                continue

        if not valid_nodes:
            raise ValueError("No valid nodes in graph")

        node_ids: Set[str] = {n.id for n in valid_nodes}
        raw_edges = data.get("edges", [])
        valid_edges: List[MisconceptionEdge] = []
        for raw in raw_edges:
            try:
                src = str(raw["source"])
                tgt = str(raw["target"])
                etype = str(raw.get("type", "related"))
                if etype not in ("prerequisite", "related"):
                    continue
                if src == tgt:  # self-loop
                    continue
                if src not in node_ids or tgt not in node_ids:  # orphan
                    continue
                valid_edges.append(MisconceptionEdge(source=src, target=tgt, type=etype))  # type: ignore[arg-type]
            except (KeyError, TypeError):
                continue

        # Strip cycles among prerequisite edges
        valid_edges = self._remove_cycles(valid_edges, node_ids)

        return MisconceptionGraph(nodes=valid_nodes, edges=valid_edges)

    def _remove_cycles(
        self, edges: List[MisconceptionEdge], node_ids: Set[str]
    ) -> List[MisconceptionEdge]:
        """Drop prerequisite edges that would create a cycle. Greedy DFS check.

        Related edges are undirected in spirit, so they don't create cycles.
        """
        accepted: List[MisconceptionEdge] = []
        adjacency: Dict[str, Set[str]] = {n: set() for n in node_ids}
        for e in edges:
            if e.type != "prerequisite":
                accepted.append(e)
                continue
            # Tentatively add and check for cycle starting from target reaching source
            adjacency[e.source].add(e.target)
            if self._reachable(adjacency, e.target, e.source):
                # cycle — reject
                adjacency[e.source].discard(e.target)
                continue
            accepted.append(e)
        return accepted

    def _reachable(self, adj: Dict[str, Set[str]], start: str, target: str) -> bool:
        seen: Set[str] = set()
        stack = [start]
        while stack:
            n = stack.pop()
            if n == target:
                return True
            if n in seen:
                continue
            seen.add(n)
            stack.extend(adj.get(n, set()))
        return False

    def _fallback(self, problem: Dict[str, Any]) -> MisconceptionGraph:
        """Used when the LLM call fails or returns invalid JSON.

        Synthesise a single node from bug_desc so the socratic flow can still run.
        """
        desc = problem.get("bug_desc") or "Bug present in this problem."
        node = MisconceptionNode(
            id="M1",
            name="Primary misconception",
            description=desc,
            concept="general",
            type="conceptual",
        )
        return MisconceptionGraph(nodes=[node], edges=[])
