from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Protocol

from django.contrib.auth.models import User

from finance.models import Category, Expense, Income, VoiceCommandLog


class TokenLike(Protocol):
    text: str
    is_space: bool


class SimpleToken:
    def __init__(self, text: str) -> None:
        self.text = text
        self.is_space = not text.strip()


class SimpleSpanishTokenizer:
    def __call__(self, text: str) -> list[SimpleToken]:
        return [SimpleToken(token) for token in re.findall(r"[\wáéíóúñü]+", text, flags=re.I)]


@dataclass(frozen=True)
class VoiceIntent:
    kind: str
    category_code: str
    category_name: str
    amount: Decimal
    concept: str


def _load_nlp():
    try:
        import spacy
    except Exception:
        return SimpleSpanishTokenizer()

    try:
        return spacy.load("es_core_news_sm")
    except Exception:
        try:
            return spacy.blank("es")
        except Exception:
            return SimpleSpanishTokenizer()


NLP = _load_nlp()


CATEGORY_RULES = {
    "food": {
        "name": "Alimentacion",
        "icon": "utensils",
        "color": "#f97316",
        "terms": {"alimentacion", "comida", "comidas", "almuerzo", "desayuno", "cena", "mercado", "restaurante", "cafeteria"},
    },
    "transport": {
        "name": "Transporte",
        "icon": "bus",
        "color": "#0ea5e9",
        "terms": {"transporte", "bus", "taxi", "uber", "gasolina", "metro", "pasaje", "peaje"},
    },
    "health": {
        "name": "Salud",
        "icon": "heart-pulse",
        "color": "#dc2626",
        "terms": {"salud", "medicina", "medico", "farmacia", "hospital", "odontologia"},
    },
    "entertainment": {
        "name": "Entretenimiento",
        "icon": "party-popper",
        "color": "#db2777",
        "terms": {"entretenimiento", "cine", "netflix", "spotify", "juego", "salida", "concierto"},
    },
    "housing": {
        "name": "Vivienda",
        "icon": "home",
        "color": "#8b5cf6",
        "terms": {"vivienda", "arriendo", "renta", "hipoteca", "casa", "apartamento"},
    },
    "education": {
        "name": "Educacion",
        "icon": "graduation-cap",
        "color": "#2563eb",
        "terms": {"educacion", "estudio", "universidad", "colegio", "curso", "libro", "matricula"},
    },
    "services": {
        "name": "Servicios",
        "icon": "plug",
        "color": "#64748b",
        "terms": {"servicios", "luz", "agua", "internet", "telefono", "energia", "gas"},
    },
    "savings": {
        "name": "Ahorro",
        "icon": "piggy-bank",
        "color": "#059669",
        "terms": {"ahorro", "ahorros", "inversion", "inversiones", "fondo"},
    },
    "other": {
        "name": "Otros",
        "icon": "circle-ellipsis",
        "color": "#475569",
        "terms": {"otro", "otros", "varios", "general"},
    },
}

EXPENSE_TERMS = {
    "gaste",
    "gasto",
    "gastar",
    "pague",
    "pago",
    "pagar",
    "compre",
    "compra",
    "egreso",
    "salio",
}
INCOME_TERMS = {
    "recibi",
    "recibir",
    "ingrese",
    "ingreso",
    "entraron",
    "cobre",
    "cobro",
    "salario",
    "sueldo",
    "pago",
    "honorarios",
}

UNITS = {
    "cero": 0,
    "un": 1,
    "uno": 1,
    "una": 1,
    "dos": 2,
    "tres": 3,
    "cuatro": 4,
    "cinco": 5,
    "seis": 6,
    "siete": 7,
    "ocho": 8,
    "nueve": 9,
}
SPECIALS = {
    "diez": 10,
    "once": 11,
    "doce": 12,
    "trece": 13,
    "catorce": 14,
    "quince": 15,
    "dieciseis": 16,
    "diecisiete": 17,
    "dieciocho": 18,
    "diecinueve": 19,
    "veinte": 20,
    "veintiuno": 21,
    "veintidos": 22,
    "veintitres": 23,
    "veinticuatro": 24,
    "veinticinco": 25,
    "veintiseis": 26,
    "veintisiete": 27,
    "veintiocho": 28,
    "veintinueve": 29,
}
TENS = {"treinta": 30, "cuarenta": 40, "cincuenta": 50, "sesenta": 60, "setenta": 70, "ochenta": 80, "noventa": 90}
HUNDREDS = {
    "cien": 100,
    "ciento": 100,
    "doscientos": 200,
    "trescientos": 300,
    "cuatrocientos": 400,
    "quinientos": 500,
    "seiscientos": 600,
    "setecientos": 700,
    "ochocientos": 800,
    "novecientos": 900,
}
NUMBER_WORDS = set(UNITS) | set(SPECIALS) | set(TENS) | set(HUNDREDS) | {"y", "mil", "millon", "millones"}
CURRENCY_WORDS = {"peso", "pesos", "cop", "colombianos"}


def _strip_accents(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.lower())
    return "".join(char for char in normalized if not unicodedata.combining(char))


def _tokens(command: str) -> list[str]:
    doc = NLP(_strip_accents(command))
    return [token.text for token in doc if not token.is_space and token.text.strip()]


def _parse_numeric_amount(command: str) -> Decimal | None:
    match = re.search(r"(?<!\w)(\d{1,3}(?:[.,]\d{3})+|\d+)(?:[.,]\d{1,2})?(?!\w)", command)
    if not match:
        return None
    amount_text = match.group(0)
    if re.fullmatch(r"\d{1,3}(?:[.,]\d{3})+", amount_text):
        amount_text = amount_text.replace(".", "").replace(",", "")
    elif re.fullmatch(r"\d+[.,]\d{1,2}", amount_text):
        amount_text = amount_text.replace(",", ".")
    try:
        amount = Decimal(amount_text)
    except InvalidOperation:
        return None
    return amount if amount > 0 else None


def _parse_number_words(words: list[str]) -> int | None:
    total = 0
    current = 0
    found = False

    for word in words:
        if word in CURRENCY_WORDS or word == "y":
            continue
        if word in UNITS:
            current += UNITS[word]
            found = True
        elif word in SPECIALS:
            current += SPECIALS[word]
            found = True
        elif word in TENS:
            current += TENS[word]
            found = True
        elif word in HUNDREDS:
            current += HUNDREDS[word]
            found = True
        elif word == "mil":
            total += (current or 1) * 1000
            current = 0
            found = True
        elif word in {"millon", "millones"}:
            total += (current or 1) * 1_000_000
            current = 0
            found = True
        else:
            return None

    value = total + current
    return value if found and value > 0 else None


def _parse_spoken_amount(tokens: list[str]) -> Decimal | None:
    best: int | None = None
    for start in range(len(tokens)):
        if tokens[start] not in NUMBER_WORDS:
            continue
        phrase: list[str] = []
        for end in range(start, min(len(tokens), start + 8)):
            token = tokens[end]
            if token not in NUMBER_WORDS and token not in CURRENCY_WORDS:
                break
            phrase.append(token)
            parsed = _parse_number_words(phrase)
            if parsed and (best is None or parsed > best):
                best = parsed
    return Decimal(best) if best else None


def extract_amount(command: str, tokens: list[str]) -> Decimal:
    amount = _parse_numeric_amount(command) or _parse_spoken_amount(tokens)
    if not amount:
        raise ValueError("No pude detectar el monto del comando.")
    return amount


def detect_kind(tokens: list[str]) -> str:
    text = " ".join(tokens)
    if "registrar gasto" in text or any(token in EXPENSE_TERMS for token in tokens):
        return "expense"
    if "registrar ingreso" in text or "recibi" in tokens or "ingrese" in tokens or any(token in INCOME_TERMS for token in tokens):
        return "income"
    raise ValueError("No pude detectar si el comando es ingreso o gasto.")


def detect_category(tokens: list[str], kind: str) -> tuple[str, str]:
    token_set = set(tokens)
    for code, rule in CATEGORY_RULES.items():
        if token_set & rule["terms"]:
            return code, rule["name"]
    if kind == "income" and ({"salario", "sueldo", "honorarios"} & token_set):
        return "savings", CATEGORY_RULES["savings"]["name"]
    return "other", CATEGORY_RULES["other"]["name"]


def parse_voice_command(command: str) -> VoiceIntent:
    normalized = " ".join(command.strip().split())
    if not normalized:
        raise ValueError("El comando no puede estar vacio.")

    tokens = _tokens(normalized)
    kind = detect_kind(tokens)
    category_code, category_name = detect_category(tokens, kind)
    amount = extract_amount(normalized, tokens)

    return VoiceIntent(kind=kind, category_code=category_code, category_name=category_name, amount=amount, concept=normalized)


def find_category(user: User, category_code: str, kind: str) -> Category:
    rule = CATEGORY_RULES[category_code]
    api_kind = Category.Kind.EXPENSE if kind == "expense" else Category.Kind.INCOME
    name = rule["name"]
    qs = Category.objects.filter(name__iexact=name).filter(user__isnull=True) | Category.objects.filter(user=user, name__iexact=name)
    category = qs.filter(kind__in=[api_kind, Category.Kind.BOTH]).first()
    if category:
        return category
    return Category.objects.create(
        user=user,
        name=name,
        kind=api_kind,
        icon=rule["icon"],
        color=rule["color"],
    )


def execute_voice_command(user: User, command: str) -> dict:
    log = VoiceCommandLog.objects.create(user=user, raw_command=command)
    try:
        intent = parse_voice_command(command)
        category = find_category(user, intent.category_code, intent.kind)
        if intent.kind == "expense":
            obj = Expense.objects.create(user=user, category=category, amount=intent.amount, merchant=intent.concept)
        else:
            obj = Income.objects.create(user=user, category=category, amount=intent.amount, source=intent.concept)

        log.interpreted_type = intent.kind
        log.interpreted_category = category.name
        log.interpreted_amount = intent.amount
        log.success = True
        log.response = f"{category.name} por {intent.amount} registrado correctamente."
        log.save(update_fields=["interpreted_type", "interpreted_category", "interpreted_amount", "success", "response"])
        return {
            "success": True,
            "transaction_created": True,
            "type": intent.kind,
            "category": intent.category_code,
            "category_name": category.name,
            "amount": int(intent.amount),
            "id": obj.id,
            "message": log.response,
        }
    except ValueError as exc:
        log.response = str(exc)
        log.save(update_fields=["response"])
        return {
            "success": False,
            "transaction_created": False,
            "message": str(exc),
        }
