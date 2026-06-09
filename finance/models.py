from __future__ import annotations

from decimal import Decimal

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Profile(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    full_name = models.CharField(max_length=160, blank=True)
    phone = models.CharField(max_length=40, blank=True)
    monthly_saving_goal = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))

    def __str__(self) -> str:
        return self.full_name or self.user.get_username()


class Category(TimeStampedModel):
    class Kind(models.TextChoices):
        INCOME = "income", "Ingreso"
        EXPENSE = "expense", "Gasto"
        BOTH = "both", "Ambos"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="categories", null=True, blank=True)
    name = models.CharField(max_length=80)
    kind = models.CharField(max_length=12, choices=Kind.choices, default=Kind.BOTH)
    icon = models.CharField(max_length=40, default="circle-dollar-sign")
    color = models.CharField(max_length=20, default="#2563eb")
    is_default = models.BooleanField(default=False)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["user", "name", "kind"], name="unique_user_category_kind"),
            models.UniqueConstraint(
                fields=["name", "kind"],
                condition=Q(user__isnull=True),
                name="unique_default_category_kind",
            ),
        ]
        indexes = [
            models.Index(fields=["user", "kind"]),
            models.Index(fields=["is_default"]),
        ]

    def __str__(self) -> str:
        return self.name


class TransactionQuerySet(models.QuerySet):
    def for_user(self, user: User) -> "TransactionQuerySet":
        return self.filter(user=user).select_related("category")

    def current_month(self) -> "TransactionQuerySet":
        today = timezone.localdate()
        return self.filter(date__year=today.year, date__month=today.month)


class Income(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="incomes")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="incomes")
    amount = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    source = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    date = models.DateField(default=timezone.localdate)

    objects = TransactionQuerySet.as_manager()

    class Meta:
        ordering = ["-date", "-created_at"]
        indexes = [
            models.Index(fields=["user", "date"]),
            models.Index(fields=["category", "date"]),
        ]

    def __str__(self) -> str:
        return f"{self.source} - {self.amount}"


class Expense(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="expenses")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="expenses")
    amount = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    merchant = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    date = models.DateField(default=timezone.localdate)

    objects = TransactionQuerySet.as_manager()

    class Meta:
        ordering = ["-date", "-created_at"]
        indexes = [
            models.Index(fields=["user", "date"]),
            models.Index(fields=["category", "date"]),
        ]

    def __str__(self) -> str:
        return f"{self.merchant} - {self.amount}"


class Budget(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="budgets")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="budgets")
    month = models.PositiveSmallIntegerField()
    year = models.PositiveIntegerField()
    limit = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])

    class Meta:
        ordering = ["-year", "-month", "category__name"]
        constraints = [models.UniqueConstraint(fields=["user", "category", "month", "year"], name="unique_budget_period")]
        indexes = [models.Index(fields=["user", "year", "month"])]

    @property
    def spent(self) -> Decimal:
        total = self.user.expenses.filter(category=self.category, date__year=self.year, date__month=self.month).aggregate(
            total=models.Sum("amount")
        )["total"]
        return total or Decimal("0.00")

    @property
    def consumed_percent(self) -> Decimal:
        if self.limit == 0:
            return Decimal("0.00")
        return min((self.spent / self.limit) * Decimal("100"), Decimal("999.00"))


class Notification(TimeStampedModel):
    class Level(models.TextChoices):
        INFO = "info", "Informacion"
        WARNING = "warning", "Advertencia"
        DANGER = "danger", "Critica"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=120)
    message = models.TextField()
    level = models.CharField(max_length=16, choices=Level.choices, default=Level.INFO)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "is_read", "-created_at"])]


class Report(TimeStampedModel):
    class Format(models.TextChoices):
        PDF = "pdf", "PDF"
        EXCEL = "xlsx", "Excel"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reports")
    name = models.CharField(max_length=140)
    format = models.CharField(max_length=8, choices=Format.choices)
    filters = models.JSONField(default=dict, blank=True)
    file = models.FileField(upload_to="reports/", blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "-created_at"])]


class VoiceCommandLog(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="voice_commands")
    raw_command = models.CharField(max_length=255)
    interpreted_type = models.CharField(max_length=20, blank=True)
    interpreted_category = models.CharField(max_length=80, blank=True)
    interpreted_amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    success = models.BooleanField(default=False)
    response = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "-created_at"]), models.Index(fields=["success"])]
