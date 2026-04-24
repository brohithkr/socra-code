from __future__ import annotations

import unittest

import httpx
from fastapi.testclient import TestClient

from backend.main import app
from backend.api import practice


class FailingPipeline:
    async def run(
        self,
        code: str,
        error: str | None,
        history: list[str],
        session_id: str,
        candidate_count: int = 5,
        verifier_use_llm: bool = True,
    ) -> tuple[str, object, float]:
        request = httpx.Request("POST", "https://openrouter.ai/api/v1/chat/completions")
        response = httpx.Response(401, request=request)
        raise httpx.HTTPStatusError("401 Unauthorized", request=request, response=response)


class PracticeApiTests(unittest.TestCase):
    def setUp(self) -> None:
        app.dependency_overrides[practice.get_pipeline] = lambda: FailingPipeline()
        self.client = TestClient(app)

    def tearDown(self) -> None:
        app.dependency_overrides.clear()

    def test_hint_returns_gateway_error_for_upstream_llm_failure(self) -> None:
        response = self.client.post(
            "/hint",
            json={
                "language": "python",
                "code": "print('hi')",
                "error": None,
                "history": [],
            },
        )

        self.assertEqual(response.status_code, 502)
        self.assertEqual(
            response.json(),
            {"detail": "LLM provider request failed with status 401."},
        )
