from __future__ import annotations

from decimal import Decimal

from django.contrib.auth.models import User
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone


def _money(value) -> Decimal:
    return value or Decimal("0.00")


def dashboard_metrics(user: User) -> dict:
    today = timezone.localdate()
    incomes = user.incomes.all()
    expenses = user.expenses.all()
    month_incomes = incomes.filter(date__year=today.year, date__month=today.month)
    month_expenses = expenses.filter(date__year=today.year, date__month=today.month)

    total_income = _money(incomes.aggregate(total=Sum("amount"))["total"])
    total_expense = _money(expenses.aggregate(total=Sum("amount"))["total"])
    month_income = _money(month_incomes.aggregate(total=Sum("amount"))["total"])
    month_expense = _money(month_expenses.aggregate(total=Sum("amount"))["total"])

    expenses_by_category = list(
        month_expenses.values("category__name", "category__color")
        .annotate(total=Sum("amount"))
        .order_by("-total")
    )
    monthly_income = incomes.annotate(month=TruncMonth("date")).values("month").annotate(total=Sum("amount")).order_by("month")
    monthly_expense = expenses.annotate(month=TruncMonth("date")).values("month").annotate(total=Sum("amount")).order_by("month")

    return {
        "balance": total_income - total_expense,
        "month_income": month_income,
        "month_expense": month_expense,
        "savings": month_income - month_expense,
        "cash_flow": month_income - month_expense,
        "expenses_by_category": expenses_by_category,
        "monthly_income": list(monthly_income),
        "monthly_expense": list(monthly_expense),
        "recent_incomes": month_incomes[:5],
        "recent_expenses": month_expenses[:5],
    }
