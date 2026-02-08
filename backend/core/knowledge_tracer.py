from __future__ import annotations

import asyncio
from typing import Dict


class KnowledgeTracer:
    def __init__(self) -> None:
        self._state: Dict[str, Dict[str, float]] = {}
        self._lock = asyncio.Lock()

    async def snapshot(self, session_id: str) -> Dict[str, float]:
        async with self._lock:
            return dict(self._state.get(session_id, {}))

    async def update(self, session_id: str, concept: str, delta: float) -> None:
        async with self._lock:
            state = self._state.setdefault(session_id, {})
            state[concept] = max(0.0, min(1.0, state.get(concept, 0.5) + delta))

    async def note_hint(self, session_id: str, concept: str) -> None:
        await self.update(session_id, concept, -0.05)

    async def note_progress(self, session_id: str, concept: str) -> None:
        await self.update(session_id, concept, 0.08)
