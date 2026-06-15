# Integrantes:
- Yurelnis Fernandez Ibañez
- Emmanuel De Jesús Crespo Moreno
- Esmeyda Dayana Peñalver Cotes
- Cristhian Cuadros

# Consult-App

Consult-App es una plataforma web de finanzas personales construida con Django 5, Django REST Framework, PostgreSQL, JWT, Tailwind CSS, Alpine.js y Chart.js. El proyecto incluye panel web responsive, apartados separados para ingresos y gastos, API REST documentada con Swagger, reportes PDF/Excel, presupuestos con alertas y registro de movimientos mediante comandos de voz.

## Arquitectura

- `consult_app/`: configuracion principal de Django, rutas globales, ASGI/WSGI.
- `finance/models.py`: entidades de dominio financiero: perfil, categorias, ingresos, gastos, presupuestos, notificaciones, reportes y logs de voz.
- `finance/services/`: casos de uso desacoplados para dashboard, alertas, asistente financiero, voz y reportes.
- `finance/api/`: serializadores, ViewSets, endpoints REST y JWT.
- `templates/`: interfaz Django Templates con Tailwind CSS, Alpine.js, Chart.js y Lucide Icons.
- `docs/voice_integrations.txt`: guia para futura integracion con Siri Shortcuts, Google Assistant y Alexa.

## Tecnologias

- Python 3.14+
- Django 5+
- Django REST Framework
- PostgreSQL
- Simple JWT
- drf-spectacular Swagger/OpenAPI
- Tailwind CSS
- Alpine.js
- Chart.js
- Docker y Docker Compose

## Ejecucion con Docker

1. Crear variables de entorno:

```bash
cp .env.example .env
```

2. Levantar la aplicacion:

```bash
docker compose up --build
```

3. Abrir:

```text
http://localhost:8000
```

El `docker-compose.yml` ejecuta automaticamente migraciones, crea categorias predeterminadas, crea un usuario demo y recolecta archivos estaticos.

Credenciales demo:

```text
usuario: demo
contrasena: demo12345
```

## Ejecucion local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_defaults --demo-user
python manage.py runserver
```

Para desarrollo local sin Docker, cambia `POSTGRES_HOST=localhost` si PostgreSQL corre en tu maquina.

## Despliegue Gratis: Render + Supabase

Esta es la ruta recomendada para publicar Consult-App como demo universitaria o portafolio:

```text
Render: backend Django con Docker
Supabase: PostgreSQL administrado
```

### 1. Crear base de datos en Supabase

1. Entra a Supabase y crea un proyecto nuevo.
2. Guarda la contrasena de la base de datos.
3. Ve a `Project Settings > Database > Connection string`.
4. Copia la cadena del `Session pooler`.
5. Usa el formato con puerto `5432` y agrega `sslmode=require` si no viene incluido:

```text
postgresql://postgres.PROJECT_REF:PASSWORD@aws-0-region.pooler.supabase.com:5432/postgres?sslmode=require
```

Notas:

- Usa el `Session pooler` para Django.
- Evita el connection string directo si tu proveedor no soporta IPv6.
- Reemplaza `PASSWORD` por la contrasena real de Supabase.

### 2. Subir el proyecto a GitHub

Desde la carpeta del proyecto:

```bash
git init
git add .
git commit -m "Initial Consult-App deployment"
git branch -M main
git remote add origin https://github.com/tu-usuario/consult-app.git
git push -u origin main
```

### 3. Crear servicio en Render

El proyecto incluye [render.yaml](./render.yaml), por lo que puedes usar Render Blueprints:

1. En Render, elige `New > Blueprint`.
2. Conecta el repositorio de GitHub.
3. Render detectara `render.yaml`.
4. Antes de desplegar, agrega la variable obligatoria:

```text
DATABASE_URL=postgresql://postgres.PROJECT_REF:PASSWORD@aws-0-region.pooler.supabase.com:5432/postgres?sslmode=require
```

El blueprint ya define:

```text
DEBUG=False
ALLOWED_HOSTS=.onrender.com
CSRF_TRUSTED_ORIGINS=https://*.onrender.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### 4. Primer despliegue

Render ejecutara automaticamente:

```bash
python manage.py migrate
python manage.py seed_defaults
```

Tambien construira la imagen Docker, recolectara estaticos y arrancara Gunicorn.

### 5. Crear usuario administrador

En Render:

1. Abre el servicio `consult-app`.
2. Entra a `Shell`.
3. Ejecuta:

```bash
python manage.py createsuperuser
```

### 6. URLs de produccion

Cuando Render termine el deploy:

```text
https://consult-app.onrender.com
https://consult-app.onrender.com/api/docs/
https://consult-app.onrender.com/admin/
```

Si cambias a un dominio propio, actualiza:

```text
ALLOWED_HOSTS=consultapp.tudominio.com
CSRF_TRUSTED_ORIGINS=https://consultapp.tudominio.com
```

### Limitaciones del plan gratis

- Render puede dormir el servicio cuando no se usa.
- La primera carga despues de inactividad puede tardar.
- Supabase gratis tiene limites de almacenamiento y uso.
- Web Speech API depende del navegador; Chrome/Edge suelen funcionar mejor que Brave.

## Usuario administrador

```bash
docker compose exec web python manage.py createsuperuser
```

Luego entra a:

```text
http://localhost:8000/admin/
```

## API y Swagger

- Swagger UI: `http://localhost:8000/api/docs/`
- OpenAPI schema: `http://localhost:8000/api/schema/`
- JWT login: `POST /api/token/`
- JWT refresh: `POST /api/token/refresh/`

Endpoints principales:

- `/api/categories/`
- `/api/incomes/`
- `/api/expenses/`
- `/api/budgets/`
- `/api/notifications/`
- `/api/reports/`
- `/api/dashboard/`
- `/api/assistant/`
- `/api/v1/voice/command`
- `/api/voice-logs/`

## Comandos de voz

Formato soportado:

```text
Registrar gasto comida 20000
Registrar gasto transporte 15000
Registrar ingreso salario 2500000
Gaste veinte mil en almuerzo
Pague quince mil de transporte
Recibi dos millones de salario
Ingrese quinientos mil pesos
```

Endpoint:

```http
POST /api/v1/voice/command
Authorization: Bearer <token>
Content-Type: application/json

{"command": "Gaste veinte mil pesos en comida"}
```

El frontend incluye un boton flotante de microfono con Web Speech API, texto reconocido en tiempo real, animacion de escucha y confirmacion visual antes de guardar.

La arquitectura futura para Siri, Google Assistant y Alexa esta documentada en `docs/voice_integrations.txt`.

## Uso de IA

Consult-App incluye un modulo de Inteligencia Artificial en `ai_assistant/` para responder preguntas financieras del usuario.

Funcionalidades:

- Responder preguntas como `¿En qué gasto más dinero?`.
- Preguntar al asistente usando el boton flotante de voz desde `/asistente/`.
- Resumir la situacion financiera mensual.
- Recomendar acciones para ahorrar.
- Detectar presupuestos cerca del limite.
- Comparar gastos contra el mes anterior.
- Analizar fotos de facturas y proponer un gasto editable antes de guardarlo.

Endpoint:

```http
POST /api/v1/assistant/ask/
Authorization: Bearer <token>
Content-Type: application/json

{"question": "¿Cuál es mi categoría más costosa?"}
```

Frontend:

```text
/asistente/
```

### Arquitectura del modulo

La IA nunca accede directamente a la base de datos. El backend consulta Django ORM, genera datos agregados y anonimizados, construye el prompt y luego llama al proveedor seleccionado.

```text
Usuario -> Backend -> Base de datos -> Datos agregados -> IA -> Respuesta
```

No se envian:

- Nombres completos.
- Correos.
- Tokens.
- Contraseñas.
- Identificadores sensibles.
- Informacion bancaria.

### Patron Strategy

El modulo usa Strategy para alternar proveedores sin cambiar la logica principal.

Contrato:

```python
AIProvider.generate(prompt: str) -> str
```

Proveedores soportados:

- `mock`: proveedor local para demo sin internet.
- `gemini`: Google Gemini con `gemini-2.5-flash`.
- `groq`: Groq con `llama-3.3-70b-versatile`.

Seleccion por variable de entorno:

```env
AI_PROVIDER=mock
```

Para Gemini:

```env
AI_PROVIDER=gemini
GEMINI_API_KEY=tu_clave
```

Para Groq:

```env
AI_PROVIDER=groq
GROQ_API_KEY=tu_clave
```

Para sustentacion universitaria se recomienda:

```env
AI_PROVIDER=mock
```

Asi la demo no depende de internet ni de claves externas.

### Observabilidad

Cada consulta registra en `AIInteractionLog`:

- Proveedor usado.
- Tiempo de respuesta.
- Tokens estimados.
- Estado de exito/error.
- Fecha de consulta.

No se almacena el prompt completo ni informacion sensible.

## Registro desde SMS y Facturas

Consult-App incluye dos flujos adicionales para registrar gastos:

### SMS manual

Ruta:

```text
/sms/
```

El usuario pega un SMS bancario, la app extrae monto y comercio con reglas locales, y el usuario selecciona la categoria antes de guardar.

Ejemplo:

```text
Compra por $35.900 en D1. Tarjeta terminada en 1234.
```

La app propone:

```text
Monto: 35900
Comercio: D1
Categoria: seleccionada por el usuario
```

### Foto de factura

Ruta:

```text
/facturas/
```

El usuario sube una imagen de factura. Si `GEMINI_API_KEY` existe, el sistema intenta extraer:

- Monto.
- Comercio.
- Categoria sugerida.
- Descripcion.

El gasto nunca se crea automaticamente. Primero se muestra una propuesta editable y el usuario confirma.

Si Gemini falla o no hay internet, se muestra un formulario manual para que la demo continue.

En Render debes configurar:

```env
GEMINI_API_KEY=tu_clave_de_gemini
```

El analizador de facturas usa Gemini cuando esa clave existe, incluso si el chat financiero usa otro proveedor.

## Reportes

La pantalla `/reportes/` permite filtrar por fecha, categoria y tipo de movimiento. Puede generar:

- PDF con ReportLab.
- Excel `.xlsx` con OpenPyXL.

## Seguridad

- CSRF activo en formularios web.
- JWT para API.
- Password hashing nativo de Django.
- ORM de Django para prevenir SQL Injection.
- Autoescape de templates para mitigar XSS.
- Variables de entorno para secretos.
- Cookies de sesion `HttpOnly`.
- `X_FRAME_OPTIONS=DENY`.

## Calidad

La logica financiera vive en servicios desacoplados para favorecer separacion de responsabilidades y pruebas. Los modelos incluyen indices por usuario, fecha, categoria y estado para consultas frecuentes. La UI usa componentes consistentes, estados vacios, focus visible y estructura mobile first.

## Pruebas

```bash
python manage.py test
```

## Capturas sugeridas para entrega

- Dashboard con metricas y graficas.
- Apartados independientes de ingresos y gastos.
- Formulario de comando de voz registrando una transaccion.
- Presupuestos con barra de consumo y alertas.
- Reporte PDF/Excel descargado.
- Swagger UI con endpoints documentados.

## Flujo del sistema

1. El usuario se registra o inicia sesion.
2. El sistema crea su perfil automaticamente.
3. El usuario registra ingresos, gastos y categorias.
4. El dashboard calcula balance, gastos del mes, ahorro y flujo de caja.
5. Los presupuestos disparan alertas al 80%, 90% y 100%.
6. El asistente financiero resume patrones y recomendaciones.
7. Los reportes exportan movimientos filtrados.
8. El endpoint de voz interpreta frases simples y registra transacciones auditables.
