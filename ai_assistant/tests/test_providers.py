from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase, override_settings

from ai_assistant.providers.gemini_provider import GeminiProvider
from ai_assistant.providers.groq_provider import GroqProvider
from ai_assistant.providers.mock_provider import MockProvider


class ProviderTests(SimpleTestCase):
    def test_mock_provider_returns_text(self):
        self.assertIn("gastos", MockProvider().generate("categorias_top"))

    @override_settings(GEMINI_API_KEY="fake", AI_MAX_RETRIES=0)
    @patch("google.genai.Client")
    def test_gemini_provider_uses_sdk(self, client_cls):
        client = client_cls.return_value
        client.models.generate_content.return_value = MagicMock(text="respuesta")
        self.assertEqual(GeminiProvider().generate("hola"), "respuesta")

    @override_settings(GROQ_API_KEY="fake", AI_TIMEOUT_SECONDS=5, AI_MAX_RETRIES=0)
    @patch("groq.Groq")
    def test_groq_provider_uses_sdk(self, groq_cls):
        message = MagicMock(content="respuesta")
        choice = MagicMock(message=message)
        groq_cls.return_value.chat.completions.create.return_value = MagicMock(choices=[choice])
        self.assertEqual(GroqProvider().generate("hola"), "respuesta")
