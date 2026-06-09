from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AssistantAPIView,
    BudgetViewSet,
    CategoryViewSet,
    DashboardAPIView,
    ExpenseViewSet,
    IncomeViewSet,
    NotificationViewSet,
    ProfileViewSet,
    ReportViewSet,
    VoiceCommandAPIView,
    VoiceCommandLogViewSet,
)

router = DefaultRouter()
router.register("profiles", ProfileViewSet, basename="profiles")
router.register("categories", CategoryViewSet, basename="categories")
router.register("incomes", IncomeViewSet, basename="incomes")
router.register("expenses", ExpenseViewSet, basename="expenses")
router.register("budgets", BudgetViewSet, basename="budgets")
router.register("notifications", NotificationViewSet, basename="notifications")
router.register("reports", ReportViewSet, basename="reports")
router.register("voice-logs", VoiceCommandLogViewSet, basename="voice-logs")

urlpatterns = [
    path("", include(router.urls)),
    path("dashboard/", DashboardAPIView.as_view(), name="api-dashboard"),
    path("assistant/", AssistantAPIView.as_view(), name="api-assistant"),
    path("voice-command/", VoiceCommandAPIView.as_view(), name="api-voice-command"),
    path("v1/voice/command", VoiceCommandAPIView.as_view(), name="api-v1-voice-command"),
]
