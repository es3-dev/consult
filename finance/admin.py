from django.contrib import admin

from .models import Budget, Category, Expense, Income, Notification, Profile, Report, VoiceCommandLog


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "full_name", "monthly_saving_goal")
    search_fields = ("user__username", "full_name")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "user", "is_default", "color")
    list_filter = ("kind", "is_default")
    search_fields = ("name",)


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ("user", "source", "category", "amount", "date")
    list_filter = ("category", "date")
    search_fields = ("source", "description", "user__username")


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("user", "merchant", "category", "amount", "date")
    list_filter = ("category", "date")
    search_fields = ("merchant", "description", "user__username")


admin.site.register(Budget)
admin.site.register(Notification)
admin.site.register(Report)
admin.site.register(VoiceCommandLog)
