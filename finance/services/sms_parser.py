from __future__ import annotations

import re
from decimal import Decimal


def parse_sms_expense(message: str) -> dict:
    """Extrae monto y comercio desde un SMS pegado manualmente."""
    clean = " ".join(message.strip().split())
    amount = _extract_amount(clean)
    merchant = _extract_merchant(clean)
    return {
        "raw_message": clean,
        "amount": amount,
        "merchant": merchant,
    }


def _extract_amount(text: str) -> Decimal | None:
    match = re.search(r"(?:\$|cop\s*)?(\d{1,3}(?:[.,]\d{3})+|\d+)(?:[.,]\d{1,2})?", text, re.I)
    if not match:
        return None
    value = match.group(1)
    if re.fullmatch(r"\d{1,3}(?:[.,]\d{3})+", value):
        value = value.replace(".", "").replace(",", "")
    return Decimal(value)


def _extract_merchant(text: str) -> str:
    patterns = [
        r"en\s+([A-Za-zÁÉÍÓÚÑáéíóúñ0-9 ._-]{2,40})",
        r"comercio\s+([A-Za-zÁÉÍÓÚÑáéíóúñ0-9 ._-]{2,40})",
        r"establecimiento\s+([A-Za-zÁÉÍÓÚÑáéíóúñ0-9 ._-]{2,40})",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.I)
        if match:
            merchant = match.group(1).strip(" .,-")
            merchant = re.split(r"\b(tarjeta|cuenta|aprobada|fecha|valor|ref|referencia)\b", merchant, flags=re.I)[0]
            return merchant.strip(" .,-") or "Gasto desde SMS"
    return "Gasto desde SMS"
