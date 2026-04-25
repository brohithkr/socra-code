from __future__ import annotations

from typing import Optional

import httpx
from fastapi import APIRouter, Depends
from fastapi import HTTPException

from ..core.pipeline import HintPipeline
from ..core.socratic_pipeline import SocraticPipeline
from ..deps import get_pipeline, get_problem_registry, get_socratic_pipeline
from ..execution.runner import run_code
from ..problems.registry import ProblemRegistry
from ..schemas import HintRequest, HintResponse, RunRequest, RunResponse

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
    hint = await _run_classic(request, pipeline)
    return HintResponse(hint=hint, mode="classic")


@router.post("/chat", response_model=HintResponse)
async def chat_endpoint(
    request: HintRequest,
    pipeline: HintPipeline = Depends(get_pipeline),
    socratic: SocraticPipeline = Depends(get_socratic_pipeline),
    registry: ProblemRegistry = Depends(get_problem_registry),
):
    problem: Optional[dict] = None
    if request.problem_id:
        problem = registry.get(request.problem_id)

    if _should_use_socratic(problem):
        return await _run_socratic(request, socratic, problem)
    hint = await _run_classic(request, pipeline)
    return HintResponse(hint=hint, mode="classic")


def _should_use_socratic(problem: Optional[dict]) -> bool:
    if problem is None:
        return False
    return bool(problem.get("bug_desc")) or bool(problem.get("bug_fixes"))


async def _run_classic(request: HintRequest, pipeline: HintPipeline) -> str:
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
    return hint


async def _run_socratic(
    request: HintRequest,
    socratic: SocraticPipeline,
    problem: dict,
) -> HintResponse:
    session_id = request.session_id or "practice"
    try:
        result = await socratic.run(
            session_id=session_id,
            problem=problem,
            code=request.code,
            output=request.output,
            user_message=request.user_message,
            chat_history=request.chat_history,
        )
    except httpx.HTTPStatusError as exc:
        status_code = exc.response.status_code if exc.response is not None else 502
        raise HTTPException(
            status_code=502,
            detail=f"LLM provider request failed with status {status_code}.",
        ) from exc
    return HintResponse(hint=result.hint, mode="socratic", progress=result.progress)
