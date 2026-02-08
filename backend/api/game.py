from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from ..schemas import CreateGameRequest, CreateGameResponse, RoomStateResponse
from ..store.base import Store
from ..deps import get_store

router = APIRouter()


@router.post("/create-game", response_model=CreateGameResponse)
async def create_game(request: CreateGameRequest, store: Store = Depends(get_store)):
    room = await store.create_room(language=request.language, seed_code=request.seed_code)
    return CreateGameResponse(room_id=room.room_id, state=room.to_dict())


@router.get("/room/{room_id}", response_model=RoomStateResponse)
async def get_room(room_id: str, store: Store = Depends(get_store)):
    room = await store.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return RoomStateResponse(room_id=room_id, state=room.to_dict())
