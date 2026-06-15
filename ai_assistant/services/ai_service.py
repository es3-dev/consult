from __future__ import annotations

import logging
import re
import time

from django.contrib.auth.models import User

from ai_assistant.models import AIInteractionLog
from ai_assistant.selectors.provider_selector import get_ai_provider
from ai_assistant.services.financial_context import build_financial_context
from ai_assistant.services.prompt_builder import build_prompt

logger = logging.getLogger(__name__)


class FinancialAssistantService:
    """Caso de uso principal: datos agregados -> prompt -> proveedor IA -> respuesta."""

    def ask(self, user: User, question: str) -> dict:
        started = time.perf_counter()
        clean_question = sanitize_question(question)
        provider = get_ai_provider()
        prompt = ""
        try:
            context = build_financial_context(user)
            prompt = build_prompt(clean_question, context)
            answer = provider.generate(prompt)
            elapsed = int((time.perf_counter() - started) * 1000)
            self._log(user, provider.name, clean_question, prompt, answer, elapsed, True, "")
            return {"answer": answer, "provider": provider.name}
        except Exception as exc:
            elapsed = int((time.perf_counter() - started) * 1000)
            logger.exception("Error en asistente IA")
            self._log(user, provider.name, clean_question, prompt, "", elapsed, False, str(exc)[:255])
            return {
                "answer": "No pude consultar el proveedor de IA. Puedes intentar de nuevo o usar AI_PROVIDER=mock para la demo.",
                "provider": provider.name,
                "error": str(exc),
            }

    def _log(self, user: User, provider: str, question: str, prompt: str, answer: str, elapsed: int, success: bool, error: str) -> None:
        AIInteractionLog.objects.create(
            user=user,
            provider=provider,
            question_preview=question[:160],
            response_time_ms=elapsed,
            estimated_tokens=max(1, (len(prompt) + len(answer)) // 4),
            success=success,
            error_message=error,
        )


def sanitize_question(question: str) -> str:
    cleaned = re.sub(r"[\x00-\x1f\x7f]", " ", question).strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    if len(cleaned) > 300:
        cleaned = cleaned[:300]
    return cleaned
