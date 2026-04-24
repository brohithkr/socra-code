from __future__ import annotations

import unittest

from backend.core.generator import Generator
from backend.core.planner import Plan
from backend.core.reasoner import Reasoner


class PromptBuilderTests(unittest.TestCase):
    def test_reasoner_prompt_excludes_rag_language(self) -> None:
        reasoner = Reasoner(router=object())

        prompt = reasoner._build_prompt(
            code="numbers[i]",
            error="IndexError: list index out of range",
        )

        self.assertIn("Error: IndexError: list index out of range", prompt)
        self.assertIn("Code:\nnumbers[i]", prompt)
        self.assertNotIn("RAG", prompt)
        self.assertNotIn("snippets", prompt.lower())

    def test_generator_prompt_excludes_rag_section(self) -> None:
        generator = Generator(router=object())
        plan = Plan(
            bug_class="off-by-one",
            hint_level=1,
            strategy="question",
            target_concept="loop boundary",
        )

        prompt = generator._build_prompt(
            plan=plan,
            code="numbers[i]",
            error="IndexError",
            reasoning_summary="The final index is invalid.",
        )

        self.assertIn("Reasoning summary: The final index is invalid.", prompt)
        self.assertIn("Code:\nnumbers[i]", prompt)
        self.assertNotIn("RAG", prompt)
        self.assertNotIn("internal context", prompt)

