import csv
import logging
from datetime import date, timedelta
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import render
from apps.invoices.models import Invoice
from apps.payments.models import Payment

logger = logging.getLogger("billing")

@login_required
def sales_report(request):
    start = request.GET.get("start")
    end = request.GET.get("end")
    today = date.today()
    start_date = date.fromisoformat(start) if start else today.replace(day=1)
    end_date = date.fromisoformat(end) if end else today
    invoices = Invoice.objects.select_related("customer").filter(invoice_date__range=(start_date, end_date)).order_by("-invoice_date")
    totals = invoices.aggregate(subtotal=Sum("subtotal"), tax=Sum("tax_amount"), total=Sum("grand_total"), paid=Sum("paid_amount"))
    context = {"invoices": invoices, "start_date": start_date, "end_date": end_date, "subtotal": totals["subtotal"] or Decimal("0.00"), "tax": totals["tax"] or Decimal("0.00"), "total": totals["total"] or Decimal("0.00"), "paid": totals["paid"] or Decimal("0.00")}
    return render(request, "reports/sales.html", context)

@login_required
def sales_csv(request):
    start = request.GET.get("start")
    end = request.GET.get("end")
    today = date.today()
    start_date = date.fromisoformat(start) if start else today.replace(day=1)
    end_date = date.fromisoformat(end) if end else today
    invoices = Invoice.objects.select_related("customer").filter(invoice_date__range=(start_date, end_date))
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="sales-{start_date}-{end_date}.csv"'
    writer = csv.writer(response)
    writer.writerow(["Invoice", "Customer", "Date", "Subtotal", "Tax", "Total", "Paid", "Balance", "Status"])
    for invoice in invoices:
        writer.writerow([invoice.invoice_number, invoice.customer.name, invoice.invoice_date, invoice.subtotal, invoice.tax_amount, invoice.grand_total, invoice.paid_amount, invoice.balance_due, invoice.status])
    logger.info("Sales CSV exported | user=%s | start=%s | end=%s", request.user.username, start_date, end_date)
    return response

@login_required
def collection_report(request):
    payments = Payment.objects.select_related("invoice", "invoice__customer").order_by("-payment_date")
    total = payments.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    return render(request, "reports/collection.html", {"payments": payments, "total": total})
