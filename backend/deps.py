from __future__ import annotations

from .config import settings
from .core.generator import Generator
from .core.graph_constructor import GraphConstructor
from .core.pipeline import HintPipeline
from .core.planner import Planner
from .core.question_generator import QuestionGenerator
from .core.reasoner import Reasoner
from .core.response_evaluator import ResponseEvaluator
from .core.socratic_pipeline import SocraticPipeline
from .core.student_model import StudentModelStore
from .core.traversal_engine import TraversalEngine
from .core.verifier import Verifier
from .models.router import LLMRouter
from .realtime.manager import RoomManager
from .store.base import Store
from .store.memory import MemoryStore
from .store.redis import RedisStore
from .problems.registry import ProblemRegistry

_router = LLMRouter()
_planner = Planner(_router)
_reasoner = Reasoner(_router)
_generator = Generator(_router)
_verifier = Verifier(_router)
_student_store = StudentModelStore()
_pipeline = HintPipeline(_planner, _reasoner, _generator, _verifier, _student_store)
_graph_constructor = GraphConstructor(_router)
_traversal = TraversalEngine()
_question_generator = QuestionGenerator(_router)
_response_evaluator = ResponseEvaluator(_router)
_socratic_pipeline = SocraticPipeline(
    graph_constructor=_graph_constructor,
    traversal=_traversal,
    question_generator=_question_generator,
    response_evaluator=_response_evaluator,
    student_store=_student_store,
)
_room_manager = RoomManager()
_store: Store = RedisStore(settings.redis_url) if settings.redis_url else MemoryStore()
_problem_registry = ProblemRegistry(settings.problems_path, settings.code_kb_dir)


def get_store() -> Store:
    return _store


def get_pipeline() -> HintPipeline:
    return _pipeline


def get_room_manager() -> RoomManager:
    return _room_manager


def get_problem_registry() -> ProblemRegistry:
    return _problem_registry


def get_student_store() -> StudentModelStore:
    return _student_store


def get_socratic_pipeline() -> SocraticPipeline:
    return _socratic_pipeline
