# backend/core/socratic_pipeline.py
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol

from .graph_constructor import GraphConstructor
from .misconception_graph import MisconceptionGraph
from .question_generator import QuestionGenerator
from .response_evaluator import ResponseEvaluator
from .student_model import StudentModelStore
from .traversal_engine import TraversalEngine


class ChatTurn(Protocol):
    role: str
    content: str


@dataclass
class SocraticResult:
    hint: str
    progress: Dict[str, int]  # {"resolved": int, "total": int, "level": int}


COMPLETION_MESSAGE = (
    "You've worked through all the misconceptions for this problem. "
    "Try running your code to confirm it works as expected."
)


class SocraticPipeline:
    """Orchestrates graph-based Socratic tutoring.

    On the first turn for a (session_id, problem_id) pair, builds the misconception
    graph from problem data. Subsequent turns evaluate the student's previous
    response, advance state, and generate the next question at the appropriate
    hint level.

    Holds a per-session lock for the entire pipeline run to avoid TOCTOU races
    on the StudentModel state when concurrent requests arrive for the same
    session.
    """

    def __init__(
        self,
        graph_constructor: GraphConstructor,
        traversal: TraversalEngine,
        question_generator: QuestionGenerator,
        response_evaluator: ResponseEvaluator,
        student_store: StudentModelStore,
    ) -> None:
        self.graph_constructor = graph_constructor
        self.traversal = traversal
        self.question_generator = question_generator
        self.response_evaluator = response_evaluator
        self.student_store = student_store
        self._session_locks: Dict[str, asyncio.Lock] = {}

    def _lock_for(self, session_id: str) -> asyncio.Lock:
        if session_id not in self._session_locks:
            self._session_locks[session_id] = asyncio.Lock()
        return self._session_locks[session_id]

    async def run(
        self,
        session_id: str,
        problem: Dict[str, Any],
        code: str,
        output: Optional[str],
        user_message: Optional[str],
        chat_history: List[ChatTurn],
    ) -> SocraticResult:
        async with self._lock_for(session_id):
            student = await self.student_store.get_or_create(session_id)
            problem_id = str(problem["id"])

            # Initialise / reset graph state on first turn or problem switch.
            if student.problem_id != problem_id or student.graph is None:
                student.graph = await self.graph_constructor.build(problem)
                student.problem_id = problem_id
                student.resolved_node_ids = set()
                student.hint_level = 0
                student.last_question = None
                student.current_node_id = self.traversal.pick_next(student.graph, set())

            graph: MisconceptionGraph = student.graph

            # If we have a previous question and a new student message, evaluate.
            if user_message and student.last_question and student.current_node_id:
                node = graph.node(student.current_node_id)
                if node is not None:
                    result = await self.response_evaluator.evaluate(
                        node=node,
                        previous_question=student.last_question,
                        student_response=user_message,
                    )
                    if result.understanding == "strong":
                        student.resolved_node_ids.add(student.current_node_id)
                        await self.student_store.note_progress(session_id, node.concept)
                        student.hint_level = 0
                        student.current_node_id = self.traversal.pick_next(
                            graph, student.resolved_node_ids
                        )
                    else:
                        # partial or none — escalate hint level on the same node
                        student.hint_level = min(4, student.hint_level + 1)
                        if result.understanding == "partial":
                            await self.student_store.note_progress(session_id, node.concept)

            total = len(graph.nodes)
            resolved_count = len(student.resolved_node_ids)

            # All resolved → completion message
            if student.current_node_id is None:
                progress = {"resolved": resolved_count, "total": total, "level": 0}
                student.last_question = None
                return SocraticResult(hint=COMPLETION_MESSAGE, progress=progress)

            current_node = graph.node(student.current_node_id)
            assert current_node is not None  # invariant: pick_next returns valid id

            question = await self.question_generator.generate(
                node=current_node,
                hint_level=student.hint_level,
                code=code,
                output=output,
                chat_history=chat_history,
            )
            student.last_question = question
            await self.student_store.note_hint(session_id, current_node.concept)

            progress = {
                "resolved": resolved_count,
                "total": total,
                "level": student.hint_level,
            }
            return SocraticResult(hint=question, progress=progress)
