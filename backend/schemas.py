from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Dict, List, Literal, Optional


class RunRequest(BaseModel):
    language: str = Field(..., examples=["python", "java", "cpp"])
    code: str
    stdin: Optional[str] = None


class RunResponse(BaseModel):
    ok: bool
    stdout: str
    stderr: str
    exit_code: int
    duration_ms: int


class ChatMessage(BaseModel):
    role: Literal["student", "tutor"]
    content: str


class HintRequest(BaseModel):
    language: str
    code: str
    output: Optional[str] = None
    history: List[str] = Field(default_factory=list)
    user_message: Optional[str] = None
    chat_history: List[ChatMessage] = Field(default_factory=list)
    session_id: Optional[str] = None


class HintResponse(BaseModel):
    hint: str


class CreateGameRequest(BaseModel):
    language: str = "python"
    seed_code: str = ""


class CreateGameResponse(BaseModel):
    room_id: str
    state: Dict


class RoomStateResponse(BaseModel):
    room_id: str
    state: Dict


class ProblemSummary(BaseModel):
    id: str
    title: str
    language: str
    topic: Optional[str] = None
    source: str
    kind: str


class ProblemDetail(ProblemSummary):
    statement: str
    starter_code: str
    buggy_code: Optional[str] = None
    bug_desc: Optional[str] = None
    bug_fixes: Optional[str] = None


class ProblemListResponse(BaseModel):
    items: List[ProblemSummary]


class WsEnvelope(BaseModel):
    type: str
    payload: Dict
