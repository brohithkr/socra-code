from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import List

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


@dataclass
class Settings:
    app_name: str = "Socratic Sprint"
    app_env: str = os.getenv("APP_ENV", "dev")
    api_prefix: str = os.getenv("API_PREFIX", "")
    frontend_origin: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
    cors_origins: List[str] = None

    llm_provider: str = os.getenv("LLM_PROVIDER", "openrouter")
    llm_model: str = os.getenv("LLM_MODEL", "openrouter/free")
    llm_provider_planner: str | None = os.getenv("LLM_PROVIDER_PLANNER")
    llm_provider_reasoner: str | None = os.getenv("LLM_PROVIDER_REASONER")
    llm_provider_tutor: str | None = os.getenv("LLM_PROVIDER_TUTOR")
    llm_provider_verifier: str | None = os.getenv("LLM_PROVIDER_VERIFIER")
    llm_model_planner: str | None = os.getenv("LLM_MODEL_PLANNER")
    llm_model_reasoner: str | None = os.getenv("LLM_MODEL_REASONER")
    llm_model_tutor: str | None = os.getenv("LLM_MODEL_TUTOR")
    llm_model_verifier: str | None = os.getenv("LLM_MODEL_VERIFIER")

    openrouter_api_key: str | None = os.getenv("OPENROUTER_API_KEY")
    openrouter_base_url: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    hf_api_key: str | None = os.getenv("HF_API_KEY")
    hf_base_url: str = os.getenv("HF_BASE_URL", "https://api-inference.huggingface.co")
    groq_api_key: str | None = os.getenv("GROQ_API_KEY")
    groq_base_url: str = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")

    runner_mode: str = os.getenv("RUNNER_MODE", "docker")
    container_runtime: str = os.getenv("CONTAINER_RUNTIME", "docker")
    runner_fallback_to_local: bool = os.getenv("RUNNER_FALLBACK_TO_LOCAL", "true").lower() == "true"
    max_run_seconds: float = float(os.getenv("MAX_RUN_SECONDS", "5"))

    redis_url: str | None = os.getenv("REDIS_URL")

    code_kb_dir: Path = Path(os.getenv("CODE_KB_DIR", str(BASE_DIR / "codeKnowledgebase")))
    hint_candidate_count: int = int(os.getenv("HINT_CANDIDATE_COUNT", "3"))
    verifier_parallelism: int = int(os.getenv("VERIFIER_PARALLELISM", "3"))

    problems_path: Path = Path(os.getenv("PROBLEMS_PATH", str(BASE_DIR / "problems" / "data" / "problems.jsonl")))

    def __post_init__(self) -> None:
        if self.cors_origins is None:
            extra = os.getenv("CORS_ORIGINS", "")
            origins = [self.frontend_origin]
            if extra:
                origins.extend([o.strip() for o in extra.split(",") if o.strip()])
            self.cors_origins = origins


settings = Settings()
