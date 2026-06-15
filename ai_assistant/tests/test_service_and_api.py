from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from finance.models import Category, Expense, Income


@override_settings(AI_PROVIDER="mock")
class AssistantServiceAndApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="ana", password="secret12345")
        self.category = Category.objects.create(name="Transporte", kind=Category.Kind.BOTH, is_default=True)
        Income.objects.create(user=self.user, category=self.category, source="Salario", amount=Decimal("2500000"))
        Expense.objects.create(user=self.user, category=self.category, merchant="Bus", amount=Decimal("200000"))

    def test_ask_endpoint_requires_auth(self):
        response = APIClient().post("/api/v1/assistant/ask/", {"question": "¿Estoy ahorrando?"}, format="json")
        self.assertEqual(response.status_code, 403)

    def test_ask_endpoint_returns_answer(self):
        client = APIClient()
        client.force_authenticate(self.user)
        response = client.post("/api/v1/assistant/ask/", {"question": "¿Estoy ahorrando este mes?"}, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertIn("answer", response.data)
