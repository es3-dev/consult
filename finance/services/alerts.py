from __future__ import annotations

from django.contrib.auth.models import User
from django.utils import timezone

from finance.models import Budget, Notification


def evaluate_budget_alerts(user: User) -> list[Notification]:
    today = timezone.localdate()
    created: list[Notification] = []
    budgets = Budget.objects.filter(user=user, year=today.year, month=today.month).select_related("category")

    for budget in budgets:
        percent = float(budget.consumed_percent)
        threshold = None
        level = Notification.Level.INFO
        if percent >= 100:
            threshold = "100%"
            level = Notification.Level.DANGER
        elif percent >= 90:
            threshold = "90%"
            level = Notification.Level.WARNING
        elif percent >= 80:
            threshold = "80%"
            level = Notification.Level.WARNING

        if not threshold:
            continue

        title = f"Presupuesto de {budget.category.name} al {threshold}"
        exists = Notification.objects.filter(user=user, title=title, created_at__date=today).exists()
        if not exists:
            created.append(
                Notification.objects.create(
                    user=user,
                    title=title,
                    level=level,
                    message=f"Has consumido {percent:.0f}% del presupuesto mensual de {budget.category.name}.",
                )
            )
    return created
