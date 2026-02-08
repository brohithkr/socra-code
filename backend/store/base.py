from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import time


@dataclass
class RoomState:
    room_id: str
    language: str = "python"
    code: str = ""
    players: Dict[str, str] = field(default_factory=dict)
    scores: Dict[str, int] = field(default_factory=dict)
    hints_used: Dict[str, int] = field(default_factory=dict)
    started_at: float = field(default_factory=lambda: time.time())
    updated_at: float = field(default_factory=lambda: time.time())

    def to_dict(self) -> Dict:
        return {
            "room_id": self.room_id,
            "language": self.language,
            "code": self.code,
            "players": self.players,
            "scores": self.scores,
            "hints_used": self.hints_used,
            "started_at": self.started_at,
            "updated_at": self.updated_at,
        }


class Store:
    async def create_room(self, language: str, seed_code: str) -> RoomState:
        raise NotImplementedError

    async def get_room(self, room_id: str) -> Optional[RoomState]:
        raise NotImplementedError

    async def save_room(self, room: RoomState) -> None:
        raise NotImplementedError

    async def add_player(self, room_id: str, player_id: str, name: str) -> RoomState:
        raise NotImplementedError

    async def remove_player(self, room_id: str, player_id: str) -> RoomState:
        raise NotImplementedError

    async def update_code(self, room_id: str, code: str) -> RoomState:
        raise NotImplementedError

    async def update_score(self, room_id: str, player_id: str, delta: int) -> RoomState:
        raise NotImplementedError

    async def increment_hints(self, room_id: str, player_id: str) -> RoomState:
        raise NotImplementedError
