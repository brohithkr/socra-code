from __future__ import annotations

import asyncio
from typing import Dict
from fastapi import WebSocket


class RoomManager:
    def __init__(self) -> None:
        self._connections: Dict[str, Dict[str, WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, room_id: str, player_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections.setdefault(room_id, {})[player_id] = websocket

    async def disconnect(self, room_id: str, player_id: str) -> None:
        async with self._lock:
            room = self._connections.get(room_id, {})
            room.pop(player_id, None)
            if not room:
                self._connections.pop(room_id, None)

    async def broadcast(self, room_id: str, message: dict) -> None:
        async with self._lock:
            recipients = list(self._connections.get(room_id, {}).values())
        for ws in recipients:
            await ws.send_json(message)

    async def send_to(self, room_id: str, player_id: str, message: dict) -> None:
        async with self._lock:
            ws = self._connections.get(room_id, {}).get(player_id)
        if ws:
            await ws.send_json(message)
