from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Budget, Category, Expense, Income, Profile


class TailwindFormMixin:
    default_class = (
        "w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900 "
        "shadow-sm outline-none transition focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200"
    )

    def _style_fields(self) -> None:
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", self.default_class)


class RegisterForm(TailwindFormMixin, UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(label="Nombre", max_length=80)
    last_name = forms.CharField(label="Apellido", max_length=80)

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")
        labels = {"username": "Usuario", "email": "Correo electronico"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style_fields()


class ProfileForm(TailwindFormMixin, forms.ModelForm):
    first_name = forms.CharField(label="Nombre", max_length=80)
    last_name = forms.CharField(label="Apellido", max_length=80)
    email = forms.EmailField(label="Correo electronico")

    class Meta:
        model = Profile
        fields = ("full_name", "phone", "monthly_saving_goal")
        labels = {
            "full_name": "Nombre completo",
            "phone": "Telefono",
            "monthly_saving_goal": "Meta mensual de ahorro",
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.fields["first_name"].initial = self.user.first_name
        self.fields["last_name"].initial = self.user.last_name
        self.fields["email"].initial = self.user.email
        self._style_fields()

    def save(self, commit=True):
        profile = super().save(commit=False)
        self.user.first_name = self.cleaned_data["first_name"]
        self.user.last_name = self.cleaned_data["last_name"]
        self.user.email = self.cleaned_data["email"]
        if commit:
            self.user.save()
            profile.save()
        return profile


class UserScopedModelForm(TailwindFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        if "category" in self.fields:
            self.fields["category"].queryset = Category.objects.filter(user__isnull=True) | Category.objects.filter(user=self.user)
        self._style_fields()


class IncomeForm(UserScopedModelForm):
    class Meta:
        model = Income
        fields = ("amount", "source", "category", "date", "description")
        labels = {
            "amount": "Monto",
            "source": "Fuente del ingreso",
            "category": "Categoria",
            "date": "Fecha",
            "description": "Descripcion",
        }
        widgets = {"date": forms.DateInput(attrs={"type": "date"}), "description": forms.Textarea(attrs={"rows": 3})}


class ExpenseForm(UserScopedModelForm):
    class Meta:
        model = Expense
        fields = ("amount", "merchant", "category", "date", "description")
        labels = {
            "amount": "Monto",
            "merchant": "Comercio o concepto",
            "category": "Categoria",
            "date": "Fecha",
            "description": "Descripcion",
        }
        widgets = {"date": forms.DateInput(attrs={"type": "date"}), "description": forms.Textarea(attrs={"rows": 3})}


class BudgetForm(UserScopedModelForm):
    class Meta:
        model = Budget
        fields = ("category", "month", "year", "limit")
        labels = {"category": "Categoria", "month": "Mes", "year": "Ano", "limit": "Limite mensual"}


class CategoryForm(UserScopedModelForm):
    class Meta:
        model = Category
        fields = ("name", "kind", "icon", "color")
        labels = {"name": "Nombre", "kind": "Tipo", "icon": "Icono Lucide", "color": "Color"}
