from decimal import Decimal

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=80)),
                ("kind", models.CharField(choices=[("income", "Ingreso"), ("expense", "Gasto"), ("both", "Ambos")], default="both", max_length=12)),
                ("icon", models.CharField(default="circle-dollar-sign", max_length=40)),
                ("color", models.CharField(default="#2563eb", max_length=20)),
                ("is_default", models.BooleanField(default=False)),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="categories", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Profile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("full_name", models.CharField(blank=True, max_length=160)),
                ("phone", models.CharField(blank=True, max_length=40)),
                ("monthly_saving_goal", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=14)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="profile", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="Report",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=140)),
                ("format", models.CharField(choices=[("pdf", "PDF"), ("xlsx", "Excel")], max_length=8)),
                ("filters", models.JSONField(blank=True, default=dict)),
                ("file", models.FileField(blank=True, upload_to="reports/")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="reports", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="VoiceCommandLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("raw_command", models.CharField(max_length=255)),
                ("interpreted_type", models.CharField(blank=True, max_length=20)),
                ("interpreted_category", models.CharField(blank=True, max_length=80)),
                ("interpreted_amount", models.DecimalField(blank=True, decimal_places=2, max_digits=14, null=True)),
                ("success", models.BooleanField(default=False)),
                ("response", models.TextField(blank=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="voice_commands", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="Notification",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=120)),
                ("message", models.TextField()),
                ("level", models.CharField(choices=[("info", "Informacion"), ("warning", "Advertencia"), ("danger", "Critica")], default="info", max_length=16)),
                ("is_read", models.BooleanField(default=False)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="notifications", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="Income",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=14, validators=[django.core.validators.MinValueValidator(Decimal("0.01"))])),
                ("source", models.CharField(max_length=120)),
                ("description", models.TextField(blank=True)),
                ("date", models.DateField(default=django.utils.timezone.localdate)),
                ("category", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="incomes", to="finance.category")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="incomes", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-date", "-created_at"]},
        ),
        migrations.CreateModel(
            name="Expense",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=14, validators=[django.core.validators.MinValueValidator(Decimal("0.01"))])),
                ("merchant", models.CharField(max_length=120)),
                ("description", models.TextField(blank=True)),
                ("date", models.DateField(default=django.utils.timezone.localdate)),
                ("category", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="expenses", to="finance.category")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="expenses", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-date", "-created_at"]},
        ),
        migrations.CreateModel(
            name="Budget",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("month", models.PositiveSmallIntegerField()),
                ("year", models.PositiveIntegerField()),
                ("limit", models.DecimalField(decimal_places=2, max_digits=14, validators=[django.core.validators.MinValueValidator(Decimal("0.01"))])),
                ("category", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="budgets", to="finance.category")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="budgets", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-year", "-month", "category__name"]},
        ),
        migrations.AddIndex(model_name="category", index=models.Index(fields=["user", "kind"], name="finance_cat_user_id_2fbd83_idx")),
        migrations.AddIndex(model_name="category", index=models.Index(fields=["is_default"], name="finance_cat_is_defa_4a0e80_idx")),
        migrations.AddConstraint(model_name="category", constraint=models.UniqueConstraint(fields=("user", "name", "kind"), name="unique_user_category_kind")),
        migrations.AddConstraint(model_name="category", constraint=models.UniqueConstraint(condition=models.Q(("user__isnull", True)), fields=("name", "kind"), name="unique_default_category_kind")),
        migrations.AddIndex(model_name="report", index=models.Index(fields=["user", "-created_at"], name="finance_rep_user_id_10ab38_idx")),
        migrations.AddIndex(model_name="voicecommandlog", index=models.Index(fields=["user", "-created_at"], name="finance_voi_user_id_c0f020_idx")),
        migrations.AddIndex(model_name="voicecommandlog", index=models.Index(fields=["success"], name="finance_voi_success_d5e831_idx")),
        migrations.AddIndex(model_name="notification", index=models.Index(fields=["user", "is_read", "-created_at"], name="finance_not_user_id_45d5e8_idx")),
        migrations.AddIndex(model_name="income", index=models.Index(fields=["user", "date"], name="finance_inc_user_id_d99b3b_idx")),
        migrations.AddIndex(model_name="income", index=models.Index(fields=["category", "date"], name="finance_inc_categor_bf6beb_idx")),
        migrations.AddIndex(model_name="expense", index=models.Index(fields=["user", "date"], name="finance_exp_user_id_1c2f20_idx")),
        migrations.AddIndex(model_name="expense", index=models.Index(fields=["category", "date"], name="finance_exp_categor_d72aa7_idx")),
        migrations.AddIndex(model_name="budget", index=models.Index(fields=["user", "year", "month"], name="finance_bud_user_id_4ac0bd_idx")),
        migrations.AddConstraint(model_name="budget", constraint=models.UniqueConstraint(fields=("user", "category", "month", "year"), name="unique_budget_period")),
    ]
