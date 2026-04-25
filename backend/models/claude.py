from __future__ import annotations

from typing import List, Optional

from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

from .base import BaseLLMProvider


class ClaudeProvider(BaseLLMProvider):
    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key

    async def chat(self, messages: List[dict], model: str, n: int = 1, temperature: float = 0.7) -> List[str]:
        system_prompt = next((m["content"] for m in messages if m["role"] == "system"), None)
        user_messages = [m for m in messages if m["role"] != "system"]
        prompt = "\n".join(f"{m['role'].upper()}: {m['content']}" for m in user_messages)

        env = {}
        if self.api_key:
            env["ANTHROPIC_API_KEY"] = self.api_key

        results = []
        for _ in range(n):
            async for message in query(
                prompt=prompt,
                options=ClaudeAgentOptions(
                    model=model,
                    system_prompt=system_prompt,
                    max_turns=1,
                    env=env,
                ),
            ):
                if isinstance(message, ResultMessage):
                    results.append(message.result)
                    break
        return results
