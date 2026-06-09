from __future__ import annotations

from io import BytesIO

from django.contrib.auth.models import User
from django.http import HttpResponse
from openpyxl import Workbook
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def filtered_movements(user: User, filters: dict) -> list[dict]:
    rows = []
    start = filters.get("start")
    end = filters.get("end")
    category = filters.get("category")
    kind = filters.get("type")

    if kind in ("", None, "income"):
        qs = user.incomes.select_related("category").all()
        if start:
            qs = qs.filter(date__gte=start)
        if end:
            qs = qs.filter(date__lte=end)
        if category:
            qs = qs.filter(category_id=category)
        rows.extend({"type": "Ingreso", "date": i.date, "category": i.category.name, "concept": i.source, "amount": i.amount} for i in qs)

    if kind in ("", None, "expense"):
        qs = user.expenses.select_related("category").all()
        if start:
            qs = qs.filter(date__gte=start)
        if end:
            qs = qs.filter(date__lte=end)
        if category:
            qs = qs.filter(category_id=category)
        rows.extend({"type": "Gasto", "date": e.date, "category": e.category.name, "concept": e.merchant, "amount": e.amount} for e in qs)

    return sorted(rows, key=lambda row: row["date"], reverse=True)


def excel_response(user: User, filters: dict) -> HttpResponse:
    wb = Workbook()
    ws = wb.active
    ws.title = "Movimientos"
    ws.append(["Tipo", "Fecha", "Categoria", "Concepto", "Monto"])
    for row in filtered_movements(user, filters):
        ws.append([row["type"], str(row["date"]), row["category"], row["concept"], float(row["amount"])])
    stream = BytesIO()
    wb.save(stream)
    response = HttpResponse(stream.getvalue(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="consult-app-reporte.xlsx"'
    return response


def pdf_response(user: User, filters: dict) -> HttpResponse:
    stream = BytesIO()
    pdf = canvas.Canvas(stream, pagesize=letter)
    pdf.setTitle("Reporte Consult-App")
    pdf.drawString(40, 750, "Consult-App - Reporte financiero")
    y = 720
    for row in filtered_movements(user, filters)[:38]:
        pdf.drawString(40, y, f"{row['date']} | {row['type']} | {row['category']} | {row['concept']} | ${row['amount']}")
        y -= 18
        if y < 60:
            pdf.showPage()
            y = 750
    pdf.save()
    response = HttpResponse(stream.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="consult-app-reporte.pdf"'
    return response
