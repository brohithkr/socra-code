from __future__ import annotations

from typing import List

from ..config import settings
from .base import BaseLLMProvider
from .openrouter import OpenRouterProvider
from .huggingface import HuggingFaceProvider
from .groq import GroqProvider
from .mock import MockProvider
from .claude import ClaudeProvider
from .openai_provider import OpenAIProvider


class LLMRouter:
    def __init__(self) -> None:
        self.providers = {}
        if settings.openrouter_api_key:
            self.providers["openrouter"] = OpenRouterProvider(
                settings.openrouter_api_key, settings.openrouter_base_url
            )
        if settings.groq_api_key:
            self.providers["groq"] = GroqProvider(settings.groq_api_key, settings.groq_base_url)
        if settings.hf_api_key:
            self.providers["huggingface"] = HuggingFaceProvider(settings.hf_api_key, settings.hf_base_url)
        if settings.llm_provider == "mock":
            self.providers["mock"] = MockProvider()
        self.providers["claude"] = ClaudeProvider(api_key=settings.anthropic_api_key)
        if settings.openai_api_key:
            self.providers["openai"] = OpenAIProvider(settings.openai_api_key, settings.openai_base_url)

    def _pick(self, role: str) -> tuple[BaseLLMProvider, str]:
        provider_name = getattr(settings, f"llm_provider_{role}", None) or settings.llm_provider
        model_name = getattr(settings, f"llm_model_{role}", None) or settings.llm_model
        provider = self.providers.get(provider_name)
        if not provider:
            raise RuntimeError(
                f"LLM provider '{provider_name}' not configured. Set API key for {provider_name} or update LLM_PROVIDER."
            )
        return provider, model_name

    async def complete(self, role: str, system: str, prompt: str, n: int = 1, temperature: float = 0.7) -> List[str]:
        provider, model = self._pick(role)
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ]
        return await provider.chat(messages=messages, model=model, n=n, temperature=temperature)
