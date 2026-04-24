# backend/core/misconception_graph.py
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import List, Literal, Optional, Set


EdgeType = Literal["prerequisite", "related"]
NodeType = Literal["conceptual", "syntactical"]


@dataclass
class MisconceptionNode:
    id: str
    name: str
    description: str
    concept: str  # tag used as the mastery key for StudentModelStore compatibility
    type: NodeType


@dataclass
class MisconceptionEdge:
    source: str  # prerequisite node id (must be understood first if type="prerequisite")
    target: str  # node id that depends on source
    type: EdgeType


@dataclass
class MisconceptionGraph:
    nodes: List[MisconceptionNode]
    edges: List[MisconceptionEdge]

    def node(self, node_id: str) -> Optional[MisconceptionNode]:
        for n in self.nodes:
            if n.id == node_id:
                return n
        return None

    def prerequisites_of(self, node_id: str) -> Set[str]:
        return {e.source for e in self.edges if e.target == node_id and e.type == "prerequisite"}

    def all_node_ids(self) -> Set[str]:
        return {n.id for n in self.nodes}

    def to_dict(self) -> dict:
        return {
            "nodes": [asdict(n) for n in self.nodes],
            "edges": [asdict(e) for e in self.edges],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MisconceptionGraph":
        nodes = [MisconceptionNode(**n) for n in data.get("nodes", [])]
        edges = [MisconceptionEdge(**e) for e in data.get("edges", [])]
        return cls(nodes=nodes, edges=edges)
