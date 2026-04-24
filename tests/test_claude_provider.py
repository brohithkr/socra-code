from __future__ import annotations

import unittest
from unittest.mock import patch

from claude_agent_sdk import ResultMessage

from backend.models.claude import ClaudeProvider


class ClaudeProviderTests(unittest.IsolatedAsyncioTestCase):
    async def test_chat_passes_empty_env_when_api_key_is_missing(self) -> None:
        captured_options = []

        async def fake_query(*, prompt, options):
            captured_options.append(options)
            yield ResultMessage(
                subtype="success",
                duration_ms=1,
                duration_api_ms=1,
                is_error=False,
                num_turns=1,
                session_id="session-1",
                stop_reason="end_turn",
                result="stubbed response",
            )

        provider = ClaudeProvider(api_key=None)
        messages = [
            {"role": "system", "content": "System prompt"},
            {"role": "user", "content": "Hello"},
        ]

        with patch("backend.models.claude.query", fake_query):
            outputs = await provider.chat(messages=messages, model="claude-test")

        self.assertEqual(outputs, ["stubbed response"])
        self.assertEqual(captured_options[0].env, {})
