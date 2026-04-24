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
        output: str | None,
        history: list[str],
        session_id: str,
        user_message: str | None = None,
        chat_history: list | None = None,
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


class CapturingPipeline:
    def __init__(self) -> None:
        self.calls = []

    async def run(
        self,
        code: str,
        output: str | None,
        history: list[str],
        session_id: str,
        user_message: str | None = None,
        chat_history: list | None = None,
        candidate_count: int = 5,
        verifier_use_llm: bool = True,
    ) -> tuple[str, object, float]:
        self.calls.append(
            {
                "code": code,
                "output": output,
                "history": history,
                "session_id": session_id,
                "user_message": user_message,
                "chat_history": chat_history,
            }
        )
        return "What does the loop condition allow on the final iteration?", object(), 8.0


class ChatApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.pipeline = CapturingPipeline()
        app.dependency_overrides[practice.get_pipeline] = lambda: self.pipeline
        self.client = TestClient(app)

    def tearDown(self) -> None:
        app.dependency_overrides.clear()

    def test_chat_endpoint_passes_student_message_through_hint_pipeline(self) -> None:
        response = self.client.post(
            "/chat",
            json={
                "language": "python",
                "code": "for i in range(len(values) + 1): pass",
                "output": "IndexError",
                "history": ["What happens at the final index?"],
                "user_message": "I do not understand why this is out of range.",
                "chat_history": [
                    {"role": "tutor", "content": "What happens at the final index?"},
                    {"role": "student", "content": "It should read the last value."},
                ],
                "session_id": "practice-1",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"hint": "What does the loop condition allow on the final iteration?"},
        )
        self.assertEqual(
            self.pipeline.calls[0]["user_message"],
            "I do not understand why this is out of range.",
        )
        self.assertEqual(self.pipeline.calls[0]["session_id"], "practice-1")
