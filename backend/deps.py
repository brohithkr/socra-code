from __future__ import annotations

from .config import settings
from .core.generator import Generator
from .core.pipeline import HintPipeline
from .core.planner import Planner
from .core.verifier import Verifier
from .core.reasoner import Reasoner
from .core.knowledge_tracer import KnowledgeTracer
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
_tracer = KnowledgeTracer()
_pipeline = HintPipeline(_planner, _reasoner, _generator, _verifier, _tracer)
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
