from __future__ import annotations

from .base import BaseLLMProvider
from .mock import MockProvider
from .openrouter import OpenRouterProvider
from .huggingface import HuggingFaceProvider
from .groq import GroqProvider
from .claude import ClaudeProvider
from .openai_provider import OpenAIProvider
from ..config import settings


def get_provider() -> BaseLLMProvider:
    provider = settings.llm_provider.lower()
    if provider == "openrouter" and settings.openrouter_api_key:
        return OpenRouterProvider(settings.openrouter_api_key, settings.openrouter_base_url)
    if provider == "huggingface" and settings.hf_api_key:
        return HuggingFaceProvider(settings.hf_api_key, settings.hf_base_url)
    if provider == "groq" and settings.groq_api_key:
        return GroqProvider(settings.groq_api_key, settings.groq_base_url)
    if provider == "claude":
        return ClaudeProvider(api_key=settings.anthropic_api_key)
    if provider == "openai" and settings.openai_api_key:
        return OpenAIProvider(settings.openai_api_key, settings.openai_base_url)
    return MockProvider()
