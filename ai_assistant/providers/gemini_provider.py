import logging
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

from django.conf import settings

from .base import AIProvider

logger = logging.getLogger(__name__)


class GeminiProvider(AIProvider):
    name = "gemini"
    model = "gemini-2.5-flash"

    def generate(self, prompt: str) -> str:
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY no configurada.")

        from google import genai

        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        last_error: Exception | None = None
        for attempt in range(settings.AI_MAX_RETRIES + 1):
            try:
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(client.models.generate_content, model=self.model, contents=prompt)
                    response = future.result(timeout=settings.AI_TIMEOUT_SECONDS)
                return getattr(response, "text", "") or "No se genero respuesta."
            except FutureTimeoutError as exc:
                last_error = exc
                logger.warning("Gemini timeout intento %s", attempt + 1)
            except Exception as exc:
                last_error = exc
                logger.warning("Gemini fallo intento %s: %s", attempt + 1, exc)
                time.sleep(0.4 * (attempt + 1))
        raise RuntimeError(f"Gemini no disponible: {last_error}")
