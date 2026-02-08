from __future__ import annotations

import asyncio
from typing import Dict, List

from ..config import settings
from ..core.pipeline import HintPipeline
from ..models.router import LLMRouter
from ..rag.embeddings import EmbeddingModel
from .metrics import token_f1, socratic_compliance, contains_code, embed_similarity


async def evaluate_treeinstruct(
    pipeline: HintPipeline,
    router: LLMRouter,
    items: List[dict],
    embedder: EmbeddingModel,
) -> Dict[str, float]:
    totals = {
        "problem_solving": 0.0,
        "socratic_questioning": 0.0,
        "student_solution_correctness": 0.0,
        "mistake_location": 0.0,
        "mistake_correction": 0.0,
        "scaffolding_generation": 0.0,
        "pedagogy_following": 0.0,
    }
    count = 0

    for item in items:
        code = item.get("buggy_code") or item.get("starter_code") or ""
        bug_desc = item.get("bug_desc") or ""
        bug_fixes = item.get("bug_fixes") or ""
        if not code:
            continue

        hint, plan, score = await pipeline.run(
            code=code,
            error=None,
            history=[],
            session_id=f"bench:{item.get('id')}",
        )

        # Problem solving proxy: how well the hint aligns with bug description
        totals["problem_solving"] += embed_similarity(embedder, hint, bug_desc) if bug_desc else 0.0
        totals["socratic_questioning"] += 1.0 if "?" in hint else 0.0

        # Student solution correctness: ask LLM to classify correctness
        judge_prompt = (
            "Is the student's solution correct? Answer YES or NO only.\n"
            f"Bug description: {bug_desc}\n"
            f"Code:\n{code}\n"
        )
        try:
            answer = await router.complete(
                role="verifier",
                system="You are a strict correctness judge.",
                prompt=judge_prompt,
                n=1,
                temperature=0.1,
            )
            verdict = answer[0].strip().lower()
            correct = 1.0 if verdict.startswith("no") else 0.0
        except Exception:
            correct = 0.0
        totals["student_solution_correctness"] += correct

        totals["mistake_location"] += embed_similarity(embedder, hint, bug_desc) if bug_desc else 0.0
        totals["mistake_correction"] += embed_similarity(embedder, hint, bug_fixes) if bug_fixes else 0.0

        # Scaffolding: use verifier score normalized
        totals["scaffolding_generation"] += min(1.0, score / 10.0)

        pedagogy = socratic_compliance(hint)
        if contains_code(hint):
            pedagogy = max(0.0, pedagogy - 0.3)
        totals["pedagogy_following"] += pedagogy

        count += 1

    if count == 0:
        return {k: 0.0 for k in totals}

    return {k: v / count for k, v in totals.items()}
