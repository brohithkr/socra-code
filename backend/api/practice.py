from __future__ import annotations

from fastapi import APIRouter, Depends

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
    session_id = request.session_id or "practice"
    hint, plan, score = await pipeline.run(
        code=request.code,
        error=request.error,
        history=request.history,
        session_id=session_id,
    )
    return HintResponse(hint=hint, intent=plan.target_concept, score=score)
