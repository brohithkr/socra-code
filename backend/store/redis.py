from __future__ import annotations

import json
import time
import uuid
from typing import Optional

import redis.asyncio as redis

from .base import RoomState, Store


class RedisStore(Store):
    def __init__(self, redis_url: str) -> None:
        self._client = redis.from_url(redis_url, decode_responses=True)

    def _key(self, room_id: str) -> str:
        return f"game:{room_id}:state"

    async def create_room(self, language: str, seed_code: str) -> RoomState:
        room_id = uuid.uuid4().hex[:8]
        room = RoomState(room_id=room_id, language=language, code=seed_code)
        await self.save_room(room)
        return room

    async def get_room(self, room_id: str) -> Optional[RoomState]:
        raw = await self._client.get(self._key(room_id))
        if not raw:
            return None
        data = json.loads(raw)
        return RoomState(
            room_id=data["room_id"],
            language=data.get("language", "python"),
            code=data.get("code", ""),
            players=data.get("players", {}),
            scores=data.get("scores", {}),
            hints_used=data.get("hints_used", {}),
            started_at=data.get("started_at", time.time()),
            updated_at=data.get("updated_at", time.time()),
        )

    async def save_room(self, room: RoomState) -> None:
        room.updated_at = time.time()
        await self._client.set(self._key(room.room_id), json.dumps(room.to_dict()))

    async def add_player(self, room_id: str, player_id: str, name: str) -> RoomState:
        room = await self.get_room(room_id)
        if room is None:
            raise KeyError("room not found")
        room.players[player_id] = name
        room.scores.setdefault(player_id, 0)
        room.hints_used.setdefault(player_id, 0)
        await self.save_room(room)
        return room

    async def remove_player(self, room_id: str, player_id: str) -> RoomState:
        room = await self.get_room(room_id)
        if room is None:
            raise KeyError("room not found")
        room.players.pop(player_id, None)
        await self.save_room(room)
        return room

    async def update_code(self, room_id: str, code: str) -> RoomState:
        room = await self.get_room(room_id)
        if room is None:
            raise KeyError("room not found")
        room.code = code
        await self.save_room(room)
        return room

    async def update_score(self, room_id: str, player_id: str, delta: int) -> RoomState:
        room = await self.get_room(room_id)
        if room is None:
            raise KeyError("room not found")
        room.scores[player_id] = room.scores.get(player_id, 0) + delta
        await self.save_room(room)
        return room

    async def increment_hints(self, room_id: str, player_id: str) -> RoomState:
        room = await self.get_room(room_id)
        if room is None:
            raise KeyError("room not found")
        room.hints_used[player_id] = room.hints_used.get(player_id, 0) + 1
        await self.save_room(room)
        return room
