from django.test import SimpleTestCase, override_settings

from ai_assistant.providers.gemini_provider import GeminiProvider
from ai_assistant.providers.groq_provider import GroqProvider
from ai_assistant.providers.mock_provider import MockProvider
from ai_assistant.selectors.provider_selector import get_ai_provider


class ProviderSelectorTests(SimpleTestCase):
    @override_settings(AI_PROVIDER="mock")
    def test_selects_mock(self):
        self.assertIsInstance(get_ai_provider(), MockProvider)

    @override_settings(AI_PROVIDER="gemini")
    def test_selects_gemini(self):
        self.assertIsInstance(get_ai_provider(), GeminiProvider)

    @override_settings(AI_PROVIDER="groq")
    def test_selects_groq(self):
        self.assertIsInstance(get_ai_provider(), GroqProvider)
