from __future__ import annotations

import json
import logging
import re
from decimal import Decimal

from django.conf import settings

logger = logging.getLogger(__name__)


def analyze_receipt_image(image_bytes: bytes, mime_type: str) -> dict:
    """Analiza una factura sin crear gasto automaticamente."""
    if settings.AI_PROVIDER == "gemini" and settings.GEMINI_API_KEY:
        try:
            return _analyze_with_gemini(image_bytes, mime_type)
        except Exception as exc:
            logger.warning("Analisis de factura con Gemini fallo: %s", exc)
    return _mock_receipt_result()


def _analyze_with_gemini(image_bytes: bytes, mime_type: str) -> dict:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    prompt = """
Extrae datos de esta factura o recibo. Responde solo JSON valido:
{
  "amount": 0,
  "merchant": "nombre comercio o Factura",
  "category": "Alimentacion|Transporte|Salud|Entretenimiento|Vivienda|Educacion|Servicios|Ahorro|Otros",
  "description": "resumen breve"
}
No incluyas informacion bancaria ni datos personales.
""".strip()
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            prompt,
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type or "image/jpeg"),
        ],
    )
    text = getattr(response, "text", "") or "{}"
    return _normalize_result(json.loads(_extract_json(text)))


def _extract_json(text: str) -> str:
    match = re.search(r"\{.*\}", text, re.S)
    return match.group(0) if match else "{}"


def _normalize_result(data: dict) -> dict:
    amount = Decimal(str(data.get("amount") or "0"))
    return {
        "amount": float(amount) if amount > 0 else 0,
        "merchant": str(data.get("merchant") or "Factura").strip()[:120],
        "category": str(data.get("category") or "Otros").strip(),
        "description": str(data.get("description") or "Gasto detectado desde factura").strip()[:300],
    }


def _mock_receipt_result() -> dict:
    return {
        "amount": 0,
        "merchant": "Factura pendiente de confirmar",
        "category": "Otros",
        "description": "No se pudo analizar la imagen automaticamente. Completa los datos manualmente.",
    }
