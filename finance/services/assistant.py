from __future__ import annotations

from decimal import Decimal

from django.contrib.auth.models import User
from django.db.models import Sum
from django.utils import timezone


def financial_insights(user: User) -> dict:
    today = timezone.localdate()
    current_expenses = user.expenses.filter(date__year=today.year, date__month=today.month)
    current_incomes = user.incomes.filter(date__year=today.year, date__month=today.month)

    if today.month == 1:
        prev_month, prev_year = 12, today.year - 1
    else:
        prev_month, prev_year = today.month - 1, today.year

    previous_expenses = user.expenses.filter(date__year=prev_year, date__month=prev_month)
    top_category = current_expenses.values("category__name").annotate(total=Sum("amount")).order_by("-total").first()
    income_total = current_incomes.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    expense_total = current_expenses.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    previous_total = previous_expenses.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

    recommendations = []
    if top_category:
        recommendations.append(f"Tu categoria mas costosa este mes es {top_category['category__name']}.")
    if income_total > expense_total:
        recommendations.append("Estas ahorrando este mes. Mantener este margen fortalece tu liquidez.")
    else:
        recommendations.append("Tus gastos igualan o superan tus ingresos. Revisa gastos variables esta semana.")
    if previous_total and expense_total > previous_total:
        increase = ((expense_total - previous_total) / previous_total) * Decimal("100")
        recommendations.append(f"Tus gastos subieron {increase:.0f}% respecto al mes anterior.")

    near_budgets = [
        budget
        for budget in user.budgets.filter(year=today.year, month=today.month).select_related("category")
        if budget.consumed_percent >= 80
    ]

    return {
        "top_category": top_category,
        "is_saving": income_total > expense_total,
        "near_budgets": near_budgets,
        "recommendations": recommendations,
    }
