from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from ..schemas import ProblemDetail, ProblemListResponse, ProblemSummary
from ..problems.registry import ProblemRegistry
from ..deps import get_problem_registry

router = APIRouter()


@router.get("/problems", response_model=ProblemListResponse)
async def list_problems(
    language: str | None = None,
    kind: str | None = None,
    limit: int = 50,
    registry: ProblemRegistry = Depends(get_problem_registry),
):
    items = registry.list(language=language, kind=kind, limit=limit)
    summaries = [
        ProblemSummary(
            id=item["id"],
            title=item["title"],
            language=item["language"],
            topic=item.get("topic"),
            source=item.get("source", "unknown"),
            kind=item.get("kind", "unknown"),
        )
        for item in items
    ]
    return ProblemListResponse(items=summaries)


@router.get("/problems/{problem_id}", response_model=ProblemDetail)
async def get_problem(problem_id: str, registry: ProblemRegistry = Depends(get_problem_registry)):
    item = registry.get(problem_id)
    if not item:
        raise HTTPException(status_code=404, detail="Problem not found")
    return ProblemDetail(
        id=item["id"],
        title=item["title"],
        language=item["language"],
        topic=item.get("topic"),
        source=item.get("source", "unknown"),
        kind=item.get("kind", "unknown"),
        statement=item.get("statement", ""),
        starter_code=item.get("starter_code", ""),
        buggy_code=item.get("buggy_code"),
        bug_desc=item.get("bug_desc"),
        bug_fixes=item.get("bug_fixes"),
    )
