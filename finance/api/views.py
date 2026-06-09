from django.db.models import Q
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from finance.models import Budget, Category, Expense, Income, Notification, Profile, Report, VoiceCommandLog
from finance.services.alerts import evaluate_budget_alerts
from finance.services.assistant import financial_insights
from finance.services.dashboard import dashboard_metrics
from finance.services.voice import execute_voice_command

from .serializers import (
    BudgetSerializer,
    CategorySerializer,
    ExpenseSerializer,
    IncomeSerializer,
    NotificationSerializer,
    ProfileSerializer,
    ReportSerializer,
    VoiceCommandLogSerializer,
    VoiceCommandSerializer,
)


class UserOwnedMixin:
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Profile.objects.filter(user=self.request.user)


class CategoryViewSet(UserOwnedMixin, viewsets.ModelViewSet):
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.filter(Q(user=self.request.user) | Q(user__isnull=True))


class IncomeViewSet(UserOwnedMixin, viewsets.ModelViewSet):
    serializer_class = IncomeSerializer

    def get_queryset(self):
        qs = Income.objects.for_user(self.request.user)
        category = self.request.query_params.get("category")
        start = self.request.query_params.get("start")
        end = self.request.query_params.get("end")
        if category:
            qs = qs.filter(category_id=category)
        if start:
            qs = qs.filter(date__gte=start)
        if end:
            qs = qs.filter(date__lte=end)
        return qs


class ExpenseViewSet(UserOwnedMixin, viewsets.ModelViewSet):
    serializer_class = ExpenseSerializer

    def get_queryset(self):
        qs = Expense.objects.for_user(self.request.user)
        category = self.request.query_params.get("category")
        start = self.request.query_params.get("start")
        end = self.request.query_params.get("end")
        if category:
            qs = qs.filter(category_id=category)
        if start:
            qs = qs.filter(date__gte=start)
        if end:
            qs = qs.filter(date__lte=end)
        return qs


class BudgetViewSet(UserOwnedMixin, viewsets.ModelViewSet):
    serializer_class = BudgetSerializer

    def get_queryset(self):
        qs = Budget.objects.filter(user=self.request.user).select_related("category")
        month = self.request.query_params.get("month")
        year = self.request.query_params.get("year")
        if month:
            qs = qs.filter(month=month)
        if year:
            qs = qs.filter(year=year)
        return qs

    @action(detail=False, methods=["post"])
    def evaluate_alerts(self, request):
        notifications = evaluate_budget_alerts(request.user)
        return Response(NotificationSerializer(notifications, many=True).data)


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save(update_fields=["is_read"])
        return Response(self.get_serializer(notification).data)


class ReportViewSet(UserOwnedMixin, viewsets.ModelViewSet):
    serializer_class = ReportSerializer

    def get_queryset(self):
        return Report.objects.filter(user=self.request.user)


class VoiceCommandLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = VoiceCommandLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return VoiceCommandLog.objects.filter(user=self.request.user)


class VoiceCommandAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = VoiceCommandSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(execute_voice_command(request.user, serializer.validated_data["command"]))


class DashboardAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        data = dashboard_metrics(request.user)
        return Response(
            {
                "balance": data["balance"],
                "month_income": data["month_income"],
                "month_expense": data["month_expense"],
                "savings": data["savings"],
                "cash_flow": data["cash_flow"],
                "expenses_by_category": data["expenses_by_category"],
            }
        )


class AssistantAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        insights = financial_insights(request.user)
        return Response(
            {
                "top_category": insights["top_category"],
                "is_saving": insights["is_saving"],
                "near_budgets": [budget.category.name for budget in insights["near_budgets"]],
                "recommendations": insights["recommendations"],
            }
        )
