from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase

from finance.models import Expense
from finance.services.voice import execute_voice_command, parse_voice_command


class VoiceServiceTests(TestCase):
    def test_parse_expense_command(self):
        intent = parse_voice_command("Registrar gasto transporte 15000")

        self.assertEqual(intent.kind, "expense")
        self.assertEqual(intent.category_code, "transport")
        self.assertEqual(intent.amount, Decimal("15000"))

    def test_parse_spoken_expense_command(self):
        intent = parse_voice_command("Gaste veinte mil en almuerzo")

        self.assertEqual(intent.kind, "expense")
        self.assertEqual(intent.category_code, "food")
        self.assertEqual(intent.amount, Decimal("20000"))

    def test_parse_spoken_income_command(self):
        intent = parse_voice_command("Recibi dos millones de salario")

        self.assertEqual(intent.kind, "income")
        self.assertEqual(intent.category_code, "savings")
        self.assertEqual(intent.amount, Decimal("2000000"))

    def test_execute_expense_command_creates_transaction(self):
        user = User.objects.create_user(username="ana", password="secret12345")

        result = execute_voice_command(user, "Pague quince mil de transporte")

        self.assertTrue(result["success"])
        self.assertTrue(result["transaction_created"])
        self.assertEqual(result["type"], "expense")
        self.assertEqual(result["category"], "transport")
        self.assertEqual(result["amount"], 15000)
        self.assertEqual(Expense.objects.filter(user=user).count(), 1)
