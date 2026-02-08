from __future__ import annotations

from typing import List
import httpx

from .base import BaseLLMProvider


class HuggingFaceProvider(BaseLLMProvider):
    def __init__(self, api_key: str, base_url: str) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    async def chat(self, messages: List[dict], model: str, n: int = 1, temperature: float = 0.7) -> List[str]:
        # Flatten messages to a single prompt
        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "inputs": prompt,
            "parameters": {"temperature": temperature, "max_new_tokens": 200},
        }
        async with httpx.AsyncClient(timeout=40) as client:
            resp = await client.post(f"{self.base_url}/models/{model}", headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
        if isinstance(data, list) and data:
            text = data[0].get("generated_text", "")
        else:
            text = str(data)
        return [text.strip() for _ in range(n)]
