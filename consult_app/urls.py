from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from consult_app.health import health_check
from finance import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health_check, name="health"),
    path("", views.dashboard, name="dashboard"),
    path("auth/", include("django.contrib.auth.urls")),
    path("registro/", views.register, name="register"),
    path("perfil/", views.profile, name="profile"),
    path("ingresos/", views.incomes_page, name="incomes"),
    path("gastos/", views.expenses_page, name="expenses"),
    path("sms/", views.sms_import_page, name="sms-import"),
    path("facturas/", views.receipt_scan_page, name="receipt-scan"),
    path("presupuestos/", views.budgets_page, name="budgets"),
    path("reportes/", views.reports_page, name="reports"),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("asistente/", include("ai_assistant.urls")),
    path("api/v1/assistant/", include("ai_assistant.api.urls")),
    path("api/", include("finance.api.urls")),
]
