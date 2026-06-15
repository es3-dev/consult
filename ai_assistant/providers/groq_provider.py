import logging
import time

from django.conf import settings

from .base import AIProvider

logger = logging.getLogger(__name__)


class GroqProvider(AIProvider):
    name = "groq"
    model = "llama-3.3-70b-versatile"

    def generate(self, prompt: str) -> str:
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY no configurada.")

        from groq import Groq

        client = Groq(api_key=settings.GROQ_API_KEY, timeout=settings.AI_TIMEOUT_SECONDS)
        last_error: Exception | None = None
        for attempt in range(settings.AI_MAX_RETRIES + 1):
            try:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2,
                    max_tokens=450,
                )
                return response.choices[0].message.content or "No se genero respuesta."
            except Exception as exc:
                last_error = exc
                logger.warning("Groq fallo intento %s: %s", attempt + 1, exc)
                time.sleep(0.4 * (attempt + 1))
        raise RuntimeError(f"Groq no disponible: {last_error}")
