from rest_framework import serializers


class AskAssistantSerializer(serializers.Serializer):
    question = serializers.CharField(min_length=3, max_length=300, trim_whitespace=True)

    def validate_question(self, value: str) -> str:
        forbidden = ["contraseña", "password", "token", "secret_key", "api_key"]
        lowered = value.lower()
        if any(term in lowered for term in forbidden):
            raise serializers.ValidationError("La pregunta contiene terminos no permitidos.")
        return value


class AskAssistantResponseSerializer(serializers.Serializer):
    answer = serializers.CharField()
    provider = serializers.CharField()
