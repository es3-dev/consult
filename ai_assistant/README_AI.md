# Modulo de Inteligencia Artificial

El modulo `ai_assistant` agrega un asistente financiero consultable desde UI y API.

## Arquitectura

El flujo cumple privacidad por diseno:

```text
Usuario -> Backend -> Base de datos -> Datos agregados -> Proveedor IA -> Respuesta
```

La IA no accede a modelos Django ni a la base de datos. Solo recibe totales, categorias agrupadas, variaciones y presupuestos anonimizados.

## Strategy

`AIProvider` define el contrato:

```python
generate(prompt: str) -> str
```

Implementaciones:

- `MockProvider`: demo sin internet.
- `GeminiProvider`: usa `gemini-2.5-flash`.
- `GroqProvider`: usa `llama-3.3-70b-versatile`.

El selector lee `AI_PROVIDER`, por lo que cambiar proveedor no modifica el servicio principal.

## Variables

```env
AI_PROVIDER=mock
GEMINI_API_KEY=
GROQ_API_KEY=
AI_TIMEOUT_SECONDS=20
AI_MAX_RETRIES=2
AI_RATE_LIMIT_PER_MINUTE=10
```

## Endpoint

```http
POST /api/v1/assistant/ask/
Authorization: Bearer <token>

{"question": "¿En qué gasto más dinero?"}
```

## Sustentacion

Para demo estable usa:

```env
AI_PROVIDER=mock
```

Asi no dependes de internet ni de claves externas.
