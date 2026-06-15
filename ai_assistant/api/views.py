from django.conf import settings
from django.core.cache import cache
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from ai_assistant.services.ai_service import FinancialAssistantService

from .serializers import AskAssistantResponseSerializer, AskAssistantSerializer


class AskAssistantAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=AskAssistantSerializer,
        responses={200: AskAssistantResponseSerializer},
        description="Responde preguntas financieras usando contexto agregado y anonimizado.",
    )
    def post(self, request):
        key = f"ai-rate:{request.user.id}"
        count = cache.get(key, 0)
        if count >= settings.AI_RATE_LIMIT_PER_MINUTE:
            return Response({"detail": "Limite de consultas por minuto alcanzado."}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        cache.set(key, count + 1, timeout=60)

        serializer = AskAssistantSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = FinancialAssistantService().ask(request.user, serializer.validated_data["question"])
        return Response(result)
