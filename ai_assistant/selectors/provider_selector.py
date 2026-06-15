from django.conf import settings

from ai_assistant.providers.base import AIProvider
from ai_assistant.providers.gemini_provider import GeminiProvider
from ai_assistant.providers.groq_provider import GroqProvider
from ai_assistant.providers.mock_provider import MockProvider


def get_ai_provider() -> AIProvider:
    provider = settings.AI_PROVIDER.lower()
    if provider == "gemini":
        return GeminiProvider()
    if provider == "groq":
        return GroqProvider()
    return MockProvider()
