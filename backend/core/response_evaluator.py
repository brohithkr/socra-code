# backend/core/response_evaluator.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Literal

from ..models.router import LLMRouter
from .misconception_graph import MisconceptionNode
from .utils import parse_json


Understanding = Literal["none", "partial", "strong"]


# Map categorical labels to mastery deltas. Floats are not surfaced to the LLM
# — it returns labels only, so its output is well-calibrated.
UNDERSTANDING_DELTA: Dict[str, float] = {
    "none": 0.0,
    "partial": 0.15,
    "strong": 0.35,
}


@dataclass
class EvaluationResult:
    understanding: Understanding
    delta: float
    rationale: str


SYSTEM_PROMPT = "You are a strict pedagogical evaluator. Output JSON only. No prose."


def _build_prompt(
    node: MisconceptionNode,
    previous_question: str,
    student_response: str,
) -> str:
    return (
        "Evaluate the student's response for evidence of understanding the "
        "specific misconception below.\n\n"
        f"Misconception:\n  Name: {node.name}\n  Description: {node.description}\n\n"
        f"Tutor's previous question:\n{previous_question}\n\n"
        f"Student's response:\n{student_response}\n\n"
        "Rubric:\n"
        "- 'strong': clearly demonstrates awareness of the misconception. The "
        "student identifies the issue, explains the cause, or describes what "
        "should happen instead. A code fix is NOT required — directional "
        "understanding is enough.\n"
        "- 'partial': shows some awareness but not full understanding. They are "
        "on the right track but vague or incomplete.\n"
        "- 'none': appears confused, gives an unrelated answer, or just asks "
        "another question without engaging with the prior question.\n\n"
        "Return JSON:\n"
        '{"understanding": "none" | "partial" | "strong", '
        '"rationale": "1 sentence"}'
    )


class ResponseEvaluator:
    def __init__(self, router: LLMRouter) -> None:
        self.router = router

    async def evaluate(
        self,
        node: MisconceptionNode,
        previous_question: str,
        student_response: str,
    ) -> EvaluationResult:
        prompt = _build_prompt(node, previous_question, student_response)
        try:
            outputs = await self.router.complete(
                role="verifier",
                system=SYSTEM_PROMPT,
                prompt=prompt,
                n=1,
                temperature=0.1,
            )
            data = parse_json(outputs[0])
            label = str(data.get("understanding", "")).lower()
            if label not in UNDERSTANDING_DELTA:
                label = "none"
            return EvaluationResult(
                understanding=label,  # type: ignore[arg-type]
                delta=UNDERSTANDING_DELTA[label],
                rationale=str(data.get("rationale", "")),
            )
        except Exception:
            return EvaluationResult(understanding="none", delta=0.0, rationale="parse_error")
