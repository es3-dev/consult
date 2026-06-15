from django.test import SimpleTestCase, override_settings

from ai_assistant.services.receipt_analyzer import analyze_receipt_image


class ReceiptAnalyzerTests(SimpleTestCase):
    @override_settings(AI_PROVIDER="mock", GEMINI_API_KEY="")
    def test_mock_receipt_result_is_safe(self):
        result = analyze_receipt_image(b"fake", "image/jpeg")

        self.assertEqual(result["category"], "Otros")
        self.assertIn("amount", result)
