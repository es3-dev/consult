from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from finance.models import Category, Income


DEFAULT_CATEGORIES = [
    ("Alimentacion", "utensils", "#f97316"),
    ("Transporte", "bus", "#0ea5e9"),
    ("Vivienda", "home", "#8b5cf6"),
    ("Educacion", "graduation-cap", "#2563eb"),
    ("Salud", "heart-pulse", "#dc2626"),
    ("Entretenimiento", "party-popper", "#db2777"),
    ("Servicios", "plug", "#64748b"),
    ("Ahorro", "piggy-bank", "#059669"),
    ("Otros", "circle-ellipsis", "#475569"),
]


class Command(BaseCommand):
    help = "Crea categorias predeterminadas y, opcionalmente, un usuario demo."

    def add_arguments(self, parser):
        parser.add_argument("--demo-user", action="store_true", help="Crea usuario demo/demo12345 con ingreso inicial.")

    def handle(self, *args, **options):
        for name, icon, color in DEFAULT_CATEGORIES:
            Category.objects.get_or_create(
                user=None,
                name=name,
                kind=Category.Kind.BOTH,
                defaults={"icon": icon, "color": color, "is_default": True},
            )
        self.stdout.write(self.style.SUCCESS("Categorias predeterminadas listas."))

        if options["demo_user"]:
            user, created = User.objects.get_or_create(username="demo", defaults={"email": "demo@consult-app.local", "first_name": "Demo"})
            if created:
                user.set_password("demo12345")
                user.save()
            salary = Category.objects.get(name="Ahorro", user__isnull=True)
            Income.objects.get_or_create(user=user, category=salary, source="Capital inicial", amount=Decimal("2500000.00"))
            self.stdout.write(self.style.SUCCESS("Usuario demo listo: demo / demo12345"))
