import logging
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render
from .forms import PaymentForm
from .models import Payment
from apps.invoices.models import Invoice

logger = logging.getLogger("billing")

@login_required
@transaction.atomic
def payment_create(request):
    form = PaymentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        payment = form.save(commit=False)
        invoice = Invoice.objects.select_for_update().get(pk=payment.invoice_id)
        amount_after = invoice.paid_amount + payment.amount
        if payment.amount > invoice.balance_due:
            form.add_error("amount", "Payment cannot exceed the invoice balance due.")
        else:
            payment.payment_number = f"PAY-{Payment.objects.count() + 1:06d}"
            payment.save()
            invoice.paid_amount = amount_after
            invoice.recalculate()
            invoice.save(update_fields=["paid_amount", "subtotal", "tax_amount", "grand_total", "status", "updated_at"])
            logger.info("Payment received | payment=%s | invoice=%s | amount=%s | user=%s", payment.payment_number, invoice.invoice_number, payment.amount, request.user.username)
            messages.success(request, "Payment recorded successfully.")
            return redirect("invoice_detail", pk=invoice.pk)
    return render(request, "payments/form.html", {"form": form, "title": "Record Payment"})

@login_required
def payment_list(request):
    payments = Payment.objects.select_related("invoice", "invoice__customer").order_by("-payment_date", "-id")
    return render(request, "payments/list.html", {"payments": payments})
