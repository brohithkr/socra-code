# tests/test_question_generator.py
from __future__ import annotations

import unittest

from backend.core.misconception_graph import MisconceptionNode
from backend.core.question_generator import QuestionGenerator, LEVEL_PROMPTS


class FakeRouter:
    def __init__(self, response: str) -> None:
        self.response = response
        self.calls: list[dict] = []

    async def complete(self, role: str, system: str, prompt: str, n: int = 1, temperature: float = 0.7) -> list[str]:
        self.calls.append({"role": role, "system": system, "prompt": prompt, "n": n, "temperature": temperature})
        return [self.response]


NODE = MisconceptionNode(
    id="M1",
    name="Off-by-one in loop bound",
    description="Student treats range(len(x)+1) as iterating exactly len(x) times.",
    concept="loop_boundary",
    type="conceptual",
)


class QuestionGeneratorTests(unittest.IsolatedAsyncioTestCase):
    async def test_uses_tutor_role(self) -> None:
        router = FakeRouter("What happens at the last index?")
        gen = QuestionGenerator(router)
        await gen.generate(node=NODE, hint_level=0, code="x", output=None, chat_history=[])
        self.assertEqual(router.calls[0]["role"], "tutor")

    async def test_level_0_uses_open_ended_prompt(self) -> None:
        router = FakeRouter("Where could this loop go wrong?")
        gen = QuestionGenerator(router)
        await gen.generate(node=NODE, hint_level=0, code="x", output=None, chat_history=[])
        self.assertEqual(router.calls[0]["system"], LEVEL_PROMPTS[0])

    async def test_level_4_uses_reveal_prompt(self) -> None:
        router = FakeRouter("The loop runs once too many. Try fixing it.")
        gen = QuestionGenerator(router)
        await gen.generate(node=NODE, hint_level=4, code="x", output=None, chat_history=[])
        self.assertEqual(router.calls[0]["system"], LEVEL_PROMPTS[4])

    async def test_clamps_level_to_valid_range(self) -> None:
        router = FakeRouter("ok")
        gen = QuestionGenerator(router)
        await gen.generate(node=NODE, hint_level=99, code="x", output=None, chat_history=[])
        self.assertEqual(router.calls[0]["system"], LEVEL_PROMPTS[4])

        await gen.generate(node=NODE, hint_level=-5, code="x", output=None, chat_history=[])
        self.assertEqual(router.calls[1]["system"], LEVEL_PROMPTS[0])

    async def test_returns_question_text(self) -> None:
        router = FakeRouter("What if i equals len(x)?")
        gen = QuestionGenerator(router)
        q = await gen.generate(node=NODE, hint_level=0, code="x", output=None, chat_history=[])
        self.assertEqual(q, "What if i equals len(x)?")

    async def test_includes_node_and_code_in_user_prompt(self) -> None:
        router = FakeRouter("...")
        gen = QuestionGenerator(router)
        await gen.generate(
            node=NODE,
            hint_level=2,
            code="def s(): return None",
            output="IndexError",
            chat_history=[{"role": "student", "content": "huh?"}],
        )
        prompt = router.calls[0]["prompt"]
        self.assertIn("Off-by-one in loop bound", prompt)
        self.assertIn("def s(): return None", prompt)
        self.assertIn("IndexError", prompt)
        self.assertIn("huh?", prompt)
