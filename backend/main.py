from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .api.health import router as health_router
from .api.practice import router as practice_router
from .api.game import router as game_router
from .api.ws import router as ws_router
from .api.problems import router as problems_router


app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix=settings.api_prefix)
app.include_router(practice_router, prefix=settings.api_prefix)
app.include_router(game_router, prefix=settings.api_prefix)
app.include_router(ws_router, prefix=settings.api_prefix)
app.include_router(problems_router, prefix=settings.api_prefix)
