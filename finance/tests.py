from decimal import Decimal

from django.test import SimpleTestCase

from finance.services.sms_parser import parse_sms_expense


class SmsParserTests(SimpleTestCase):
    def test_extracts_amount_and_merchant(self):
        result = parse_sms_expense("Compra por $35.900 en D1. Tarjeta terminada en 1234.")

        self.assertEqual(result["amount"], Decimal("35900"))
        self.assertEqual(result["merchant"], "D1")
