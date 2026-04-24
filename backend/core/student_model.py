# backend/core/student_model.py
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Set


@dataclass
class StudentModel:
    """Per-session state. Holds both classic-mode mastery and socratic-mode graph state."""

    # Classic mode: free-form concept name -> mastery in [0.0, 1.0]
    mastery: Dict[str, float] = field(default_factory=dict)

    # Socratic mode fields. Populated on first turn of socratic flow.
    problem_id: Optional[str] = None
    graph: Optional[Any] = None  # MisconceptionGraph (avoiding import cycle)
    current_node_id: Optional[str] = None
    resolved_node_ids: Set[str] = field(default_factory=set)
    hint_level: int = 0
    last_question: Optional[str] = None


class StudentModelStore:
    """In-memory, async-locked store of StudentModel keyed by session_id.

    Replaces KnowledgeTracer. Exposes the same snapshot/note_hint/note_progress
    API used by the existing pipeline; classic mode behavior is unchanged.
    """

    def __init__(self) -> None:
        self._models: Dict[str, StudentModel] = {}
        self._lock = asyncio.Lock()

    async def get_or_create(self, session_id: str) -> StudentModel:
        async with self._lock:
            if session_id not in self._models:
                self._models[session_id] = StudentModel()
            return self._models[session_id]

    async def snapshot(self, session_id: str) -> Dict[str, float]:
        """Return a copy of the mastery dict for compatibility with HintPipeline."""
        async with self._lock:
            model = self._models.setdefault(session_id, StudentModel())
            return dict(model.mastery)

    async def note_hint(self, session_id: str, concept: str) -> None:
        await self._update(session_id, concept, -0.05)

    async def note_progress(self, session_id: str, concept: str) -> None:
        await self._update(session_id, concept, 0.08)

    async def _update(self, session_id: str, concept: str, delta: float) -> None:
        async with self._lock:
            model = self._models.setdefault(session_id, StudentModel())
            current = model.mastery.get(concept, 0.5)
            model.mastery[concept] = max(0.0, min(1.0, current + delta))
