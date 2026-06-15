from django.conf import settings
from django.db import models


class AIInteractionLog(models.Model):
    """Auditoria tecnica sin datos sensibles del usuario."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ai_interactions")
    provider = models.CharField(max_length=40)
    question_preview = models.CharField(max_length=160)
    response_time_ms = models.PositiveIntegerField(default=0)
    estimated_tokens = models.PositiveIntegerField(default=0)
    success = models.BooleanField(default=False)
    error_message = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["provider", "success"]),
        ]

    def __str__(self) -> str:
        return f"{self.provider} - {'ok' if self.success else 'error'}"
