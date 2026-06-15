from __future__ import annotations

from decimal import Decimal

from django.contrib.auth.models import User
from django.db.models import Sum
from django.utils import timezone


def _total(value) -> Decimal:
    return value or Decimal("0.00")


def build_financial_context(user: User) -> dict:
    """Devuelve solo datos agregados y anonimizados para enviar a IA."""
    today = timezone.localdate()
    month, year = today.month, today.year
    previous_month = 12 if month == 1 else month - 1
    previous_year = year - 1 if month == 1 else year

    current_expenses = user.expenses.filter(date__year=year, date__month=month).select_related("category")
    previous_expenses = user.expenses.filter(date__year=previous_year, date__month=previous_month).select_related("category")
    current_incomes = user.incomes.filter(date__year=year, date__month=month)

    income_total = _total(current_incomes.aggregate(total=Sum("amount"))["total"])
    expense_total = _total(current_expenses.aggregate(total=Sum("amount"))["total"])
    previous_expense_total = _total(previous_expenses.aggregate(total=Sum("amount"))["total"])

    top_categories = list(
        current_expenses.values("category__name")
        .annotate(total=Sum("amount"))
        .order_by("-total")[:5]
    )

    previous_categories = {
        row["category__name"]: _total(row["total"])
        for row in previous_expenses.values("category__name").annotate(total=Sum("amount"))
    }

    category_variations = []
    for row in top_categories:
        name = row["category__name"]
        current = _total(row["total"])
        previous = previous_categories.get(name, Decimal("0.00"))
        variation = None
        if previous > 0:
            variation = float(((current - previous) / previous) * Decimal("100"))
        category_variations.append({"category": name, "current": float(current), "previous": float(previous), "variation_percent": variation})

    budgets_near_limit = []
    budgets = user.budgets.filter(year=year, month=month).select_related("category")
    for budget in budgets:
        percent = budget.consumed_percent
        if percent >= 80:
            budgets_near_limit.append(
                {
                    "category": budget.category.name,
                    "limit": float(budget.limit),
                    "spent": float(budget.spent),
                    "consumed_percent": float(percent),
                }
            )

    expense_variation_percent = None
    if previous_expense_total > 0:
        expense_variation_percent = float(((expense_total - previous_expense_total) / previous_expense_total) * Decimal("100"))

    return {
        "period": {"year": year, "month": month},
        "monthly_income": float(income_total),
        "monthly_expense": float(expense_total),
        "balance": float(income_total - expense_total),
        "savings": float(income_total - expense_total),
        "top_categories": top_categories,
        "budgets_near_limit": budgets_near_limit,
        "category_variations": category_variations,
        "expense_variation_percent": expense_variation_percent,
        "privacy": "Contexto anonimo. No contiene nombres, correos, tokens ni informacion bancaria.",
    }
