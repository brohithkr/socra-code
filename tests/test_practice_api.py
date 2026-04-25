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
            {
                "hint": "What does the loop condition allow on the final iteration?",
                "mode": "classic",
                "progress": None,
            },
        )
        self.assertEqual(
            self.pipeline.calls[0]["user_message"],
            "I do not understand why this is out of range.",
        )
        self.assertEqual(self.pipeline.calls[0]["session_id"], "practice-1")


class FakeProblemRegistry:
    def __init__(self, problems: dict) -> None:
        self._problems = problems

    def get(self, problem_id: str):
        return self._problems.get(problem_id)


class FakeSocraticPipeline:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    async def run(self, *, session_id, problem, code, output, user_message, chat_history):
        from backend.core.socratic_pipeline import SocraticResult

        self.calls.append(
            {
                "session_id": session_id,
                "problem_id": problem["id"],
                "code": code,
                "output": output,
                "user_message": user_message,
            }
        )
        return SocraticResult(
            hint="What value does i hold on the last iteration?",
            progress={"resolved": 0, "total": 2, "level": 0},
        )


class ChatRoutingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.classic = CapturingPipeline()
        self.socratic = FakeSocraticPipeline()
        app.dependency_overrides[practice.get_pipeline] = lambda: self.classic
        app.dependency_overrides[practice.get_socratic_pipeline] = lambda: self.socratic
        self.client = TestClient(app)

    def tearDown(self) -> None:
        app.dependency_overrides.clear()

    def _override_registry(self, problems: dict) -> None:
        registry = FakeProblemRegistry(problems)
        app.dependency_overrides[practice.get_problem_registry] = lambda: registry

    def test_chat_uses_socratic_when_problem_has_bug_data(self) -> None:
        self._override_registry(
            {
                "p1": {
                    "id": "p1",
                    "bug_desc": "off by one",
                    "bug_fixes": "use len-1",
                    "buggy_code": "for i in range(len(xs)+1):",
                    "starter_code": "",
                }
            }
        )
        response = self.client.post(
            "/chat",
            json={
                "language": "python",
                "code": "for i in range(len(xs)+1): pass",
                "user_message": "help",
                "session_id": "s1",
                "problem_id": "p1",
            },
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["hint"], "What value does i hold on the last iteration?")
        self.assertEqual(body["mode"], "socratic")
        self.assertEqual(body["progress"], {"resolved": 0, "total": 2, "level": 0})
        self.assertEqual(self.socratic.calls[0]["problem_id"], "p1")
        self.assertEqual(self.socratic.calls[0]["session_id"], "s1")
        self.assertEqual(len(self.classic.calls), 0)

    def test_chat_falls_back_to_classic_when_no_problem_id(self) -> None:
        self._override_registry({})
        response = self.client.post(
            "/chat",
            json={
                "language": "python",
                "code": "print('hi')",
                "user_message": "help",
                "session_id": "s1",
            },
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["mode"], "classic")
        self.assertIsNone(body["progress"])
        self.assertEqual(len(self.socratic.calls), 0)
        self.assertEqual(len(self.classic.calls), 1)

    def test_chat_falls_back_to_classic_when_problem_lacks_bug_data(self) -> None:
        self._override_registry(
            {
                "p2": {
                    "id": "p2",
                    "starter_code": "",
                    # no bug_desc / bug_fixes
                }
            }
        )
        response = self.client.post(
            "/chat",
            json={
                "language": "python",
                "code": "x",
                "user_message": "help",
                "session_id": "s1",
                "problem_id": "p2",
            },
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["mode"], "classic")
        self.assertEqual(len(self.socratic.calls), 0)
        self.assertEqual(len(self.classic.calls), 1)

    def test_chat_falls_back_to_classic_when_problem_id_unknown(self) -> None:
        self._override_registry({})
        response = self.client.post(
            "/chat",
            json={
                "language": "python",
                "code": "x",
                "user_message": "help",
                "session_id": "s1",
                "problem_id": "missing",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["mode"], "classic")
        self.assertEqual(len(self.socratic.calls), 0)
