from __future__ import annotations

import time
import uuid
from typing import Dict, Optional

from .base import RoomState, Store


class MemoryStore(Store):
    def __init__(self) -> None:
        self._rooms: Dict[str, RoomState] = {}

    async def create_room(self, language: str, seed_code: str) -> RoomState:
        room_id = uuid.uuid4().hex[:8]
        room = RoomState(room_id=room_id, language=language, code=seed_code)
        self._rooms[room_id] = room
        return room

    async def get_room(self, room_id: str) -> Optional[RoomState]:
        return self._rooms.get(room_id)

    async def save_room(self, room: RoomState) -> None:
        room.updated_at = time.time()
        self._rooms[room.room_id] = room

    async def add_player(self, room_id: str, player_id: str, name: str) -> RoomState:
        room = self._rooms[room_id]
        room.players[player_id] = name
        room.scores.setdefault(player_id, 0)
        room.hints_used.setdefault(player_id, 0)
        await self.save_room(room)
        return room

    async def remove_player(self, room_id: str, player_id: str) -> RoomState:
        room = self._rooms[room_id]
        room.players.pop(player_id, None)
        await self.save_room(room)
        return room

    async def update_code(self, room_id: str, code: str) -> RoomState:
        room = self._rooms[room_id]
        room.code = code
        await self.save_room(room)
        return room

    async def update_score(self, room_id: str, player_id: str, delta: int) -> RoomState:
        room = self._rooms[room_id]
        room.scores[player_id] = room.scores.get(player_id, 0) + delta
        await self.save_room(room)
        return room

    async def increment_hints(self, room_id: str, player_id: str) -> RoomState:
        room = self._rooms[room_id]
        room.hints_used[player_id] = room.hints_used.get(player_id, 0) + 1
        await self.save_room(room)
        return room
