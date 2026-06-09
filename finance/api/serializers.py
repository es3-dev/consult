from django.contrib.auth.models import User
from rest_framework import serializers

from finance.models import Budget, Category, Expense, Income, Notification, Profile, Report, VoiceCommandLog


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name")
        read_only_fields = ("id",)


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = ("id", "user", "full_name", "phone", "monthly_saving_goal")


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "kind", "icon", "color", "is_default")
        read_only_fields = ("is_default",)


class IncomeSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Income
        fields = ("id", "category", "category_name", "amount", "source", "description", "date", "created_at")
        read_only_fields = ("created_at",)


class ExpenseSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Expense
        fields = ("id", "category", "category_name", "amount", "merchant", "description", "date", "created_at")
        read_only_fields = ("created_at",)


class BudgetSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    spent = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    consumed_percent = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)

    class Meta:
        model = Budget
        fields = ("id", "category", "category_name", "month", "year", "limit", "spent", "consumed_percent")


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ("id", "title", "message", "level", "is_read", "created_at")


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ("id", "name", "format", "filters", "file", "created_at")
        read_only_fields = ("file", "created_at")


class VoiceCommandLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoiceCommandLog
        fields = (
            "id",
            "raw_command",
            "interpreted_type",
            "interpreted_category",
            "interpreted_amount",
            "success",
            "response",
            "created_at",
        )
        read_only_fields = fields


class VoiceCommandSerializer(serializers.Serializer):
    command = serializers.CharField(max_length=255)
