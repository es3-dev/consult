from __future__ import annotations

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db.models import Q
from django.shortcuts import redirect, render
from django.utils import timezone

from .forms import BudgetForm, CategoryForm, ExpenseForm, IncomeForm, ProfileForm, RegisterForm
from .models import Budget, Category, Expense, Income
from .services.alerts import evaluate_budget_alerts
from .services.assistant import financial_insights
from .services.dashboard import dashboard_metrics
from .services.reports import excel_response, pdf_response


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.email = form.cleaned_data["email"]
            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data["last_name"]
            user.save()
            login(request, user)
            messages.success(request, "Cuenta creada. Bienvenido a Consult-App.")
            return redirect("dashboard")
    else:
        form = RegisterForm()
    return render(request, "auth/register.html", {"form": form})


@login_required
@ensure_csrf_cookie
def dashboard(request):
    evaluate_budget_alerts(request.user)
    metrics = dashboard_metrics(request.user)
    insights = financial_insights(request.user)
    categories = Category.objects.filter(Q(user=request.user) | Q(user__isnull=True))

    return render(
        request,
        "dashboard/index.html",
        {"metrics": metrics, "insights": insights, "categories": categories, "notifications": request.user.notifications.filter(is_read=False)[:5]},
    )


@login_required
@ensure_csrf_cookie
def profile(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user.profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado.")
            return redirect("profile")
    else:
        form = ProfileForm(instance=request.user.profile, user=request.user)
    return render(request, "profile/detail.html", {"form": form})


@login_required
@ensure_csrf_cookie
def incomes_page(request):
    income_form = IncomeForm(request.POST or None, user=request.user)
    category_form = CategoryForm(request.POST or None, user=request.user, prefix="category")

    action = request.POST.get("action")
    if request.method == "POST":
        if action == "income" and income_form.is_valid():
            income = income_form.save(commit=False)
            income.user = request.user
            income.save()
            messages.success(request, "Ingreso registrado.")
            return redirect("incomes")
        if action == "category" and category_form.is_valid():
            category = category_form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, "Categoria creada.")
            return redirect("incomes")

    category = request.GET.get("category")
    start = request.GET.get("start")
    end = request.GET.get("end")
    incomes = Income.objects.for_user(request.user)
    if category:
        incomes = incomes.filter(category_id=category)
    if start:
        incomes = incomes.filter(date__gte=start)
    if end:
        incomes = incomes.filter(date__lte=end)

    categories = Category.objects.filter(Q(user=request.user) | Q(user__isnull=True))
    return render(
        request,
        "finance/incomes.html",
        {
            "income_form": income_form,
            "category_form": category_form,
            "incomes": incomes[:20],
            "categories": categories,
        },
    )


@login_required
@ensure_csrf_cookie
def expenses_page(request):
    expense_form = ExpenseForm(request.POST or None, user=request.user)
    category_form = CategoryForm(request.POST or None, user=request.user, prefix="category")

    action = request.POST.get("action")
    if request.method == "POST":
        if action == "expense" and expense_form.is_valid():
            expense = expense_form.save(commit=False)
            expense.user = request.user
            expense.save()
            evaluate_budget_alerts(request.user)
            messages.success(request, "Gasto registrado.")
            return redirect("expenses")
        if action == "category" and category_form.is_valid():
            category = category_form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, "Categoria creada.")
            return redirect("expenses")

    category = request.GET.get("category")
    start = request.GET.get("start")
    end = request.GET.get("end")
    expenses = Expense.objects.for_user(request.user)
    if category:
        expenses = expenses.filter(category_id=category)
    if start:
        expenses = expenses.filter(date__gte=start)
    if end:
        expenses = expenses.filter(date__lte=end)

    categories = Category.objects.filter(Q(user=request.user) | Q(user__isnull=True))
    return render(
        request,
        "finance/expenses.html",
        {
            "expense_form": expense_form,
            "category_form": category_form,
            "expenses": expenses[:20],
            "categories": categories,
        },
    )


@login_required
@ensure_csrf_cookie
def budgets_page(request):
    form = BudgetForm(request.POST or None, user=request.user)
    if request.method == "POST" and form.is_valid():
        budget = form.save(commit=False)
        budget.user = request.user
        budget.save()
        messages.success(request, "Presupuesto guardado.")
        return redirect("budgets")

    today = timezone.localdate()
    budgets = Budget.objects.filter(user=request.user, year=today.year, month=today.month).select_related("category")
    return render(request, "finance/budgets.html", {"form": form, "budgets": budgets, "today": today})


@login_required
@ensure_csrf_cookie
def reports_page(request):
    categories = Category.objects.filter(Q(user=request.user) | Q(user__isnull=True))
    if request.GET.get("format") == "pdf":
        return pdf_response(request.user, request.GET)
    if request.GET.get("format") == "xlsx":
        return excel_response(request.user, request.GET)
    return render(request, "reports/index.html", {"categories": categories})
