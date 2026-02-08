from __future__ import annotations

import json
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from ..core.pipeline import HintPipeline
from ..execution.runner import run_code
from ..deps import get_pipeline, get_store, get_room_manager
from ..store.base import Store
from ..realtime.manager import RoomManager

router = APIRouter()


@router.websocket("/ws/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: str,
    player_id: str,
    name: str = "Anonymous",
    store: Store = Depends(get_store),
    pipeline: HintPipeline = Depends(get_pipeline),
    manager: RoomManager = Depends(get_room_manager),
):
    room = await store.get_room(room_id)
    if not room:
        await websocket.close(code=1008)
        return

    await manager.connect(room_id, player_id, websocket)
    await store.add_player(room_id, player_id, name)
    room = await store.get_room(room_id)
    await manager.broadcast(
        room_id,
        {"type": "presence", "payload": {"player_id": player_id, "name": name, "status": "joined"}},
    )

    if room:
        await manager.broadcast(
            room_id,
            {"type": "room_state", "payload": {"state": room.to_dict()}},
        )

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            msg_type = message.get("type")
            payload = message.get("payload", {})

            if msg_type == "code_update":
                code = payload.get("code", "")
                await store.update_code(room_id, code)
                await manager.broadcast(room_id, {"type": "code_update", "payload": {"code": code}})

            elif msg_type == "run_request":
                code = payload.get("code", "")
                language = payload.get("language", "python")
                ok, stdout, stderr, exit_code, duration_ms = await run_code(language=language, code=code)
                await manager.send_to(
                    room_id,
                    player_id,
                    {
                        "type": "run_result",
                        "payload": {
                            "ok": ok,
                            "stdout": stdout,
                            "stderr": stderr,
                            "exit_code": exit_code,
                            "duration_ms": duration_ms,
                        },
                    },
                )

            elif msg_type == "hint_request":
                code = payload.get("code", "")
                language = payload.get("language", "python")
                error = payload.get("error")
                history = payload.get("history", [])
                hint, plan, score = await pipeline.run(
                    code=code,
                    error=error,
                    history=history,
                    session_id=room_id,
                )
                await store.increment_hints(room_id, player_id)
                await manager.send_to(
                    room_id,
                    player_id,
                    {
                        "type": "hint_result",
                        "payload": {
                            "hint": hint,
                            "intent": plan.target_concept,
                            "score": score,
                            "language": language,
                        },
                    },
                )

            elif msg_type == "score_delta":
                delta = int(payload.get("delta", 0))
                room_state = await store.update_score(room_id, player_id, delta)
                await manager.broadcast(room_id, {"type": "score_update", "payload": {"scores": room_state.scores}})

            else:
                await manager.send_to(
                    room_id,
                    player_id,
                    {"type": "error", "payload": {"message": "Unknown message type"}},
                )

    except WebSocketDisconnect:
        await store.remove_player(room_id, player_id)
        await manager.broadcast(
            room_id,
            {"type": "presence", "payload": {"player_id": player_id, "name": name, "status": "left"}},
        )
        room = await store.get_room(room_id)
        if room:
            await manager.broadcast(
                room_id,
                {"type": "room_state", "payload": {"state": room.to_dict()}},
            )
        await manager.disconnect(room_id, player_id)
