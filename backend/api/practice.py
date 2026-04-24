from __future__ import annotations

import httpx
from fastapi import APIRouter, Depends
from fastapi import HTTPException

from ..execution.runner import run_code
from ..schemas import RunRequest, RunResponse, HintRequest, HintResponse
from ..core.pipeline import HintPipeline
from ..deps import get_pipeline

router = APIRouter()


@router.post("/run", response_model=RunResponse)
async def run_endpoint(request: RunRequest):
    ok, stdout, stderr, exit_code, duration_ms = await run_code(
        language=request.language,
        code=request.code,
        stdin=request.stdin,
    )
    return RunResponse(
        ok=ok,
        stdout=stdout,
        stderr=stderr,
        exit_code=exit_code,
        duration_ms=duration_ms,
    )


@router.post("/hint", response_model=HintResponse)
async def hint_endpoint(request: HintRequest, pipeline: HintPipeline = Depends(get_pipeline)):
    return await _run_hint_pipeline(request, pipeline)


@router.post("/chat", response_model=HintResponse)
async def chat_endpoint(request: HintRequest, pipeline: HintPipeline = Depends(get_pipeline)):
    return await _run_hint_pipeline(request, pipeline)


async def _run_hint_pipeline(request: HintRequest, pipeline: HintPipeline) -> HintResponse:
    session_id = request.session_id or "practice"
    try:
        hint, _plan, _score = await pipeline.run(
            code=request.code,
            output=request.output,
            history=request.history,
            user_message=request.user_message,
            chat_history=request.chat_history,
            session_id=session_id,
        )
    except httpx.HTTPStatusError as exc:
        status_code = exc.response.status_code if exc.response is not None else 502
        raise HTTPException(
            status_code=502,
            detail=f"LLM provider request failed with status {status_code}.",
        ) from exc
    return HintResponse(hint=hint)
