import logging
import json
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render
from apps.core.models import CompanyProfile
from apps.products.models import Product
from .forms import InvoiceForm, InvoiceItemFormSet
from .models import Invoice
from .pdf import build_invoice_pdf

logger = logging.getLogger("billing")

def _next_number():
    last = Invoice.objects.order_by("-id").first()
    return f"INV-{last.id + 1:06d}" if last else "INV-000001"

@login_required
def invoice_list(request):
    invoices = Invoice.objects.select_related("customer").all()
    return render(request, "invoices/list.html", {"invoices": invoices})

@login_required
@transaction.atomic
def invoice_create(request):
    invoice = Invoice(invoice_number=_next_number())
    form = InvoiceForm(request.POST or None, instance=invoice)
    formset = InvoiceItemFormSet(request.POST or None, instance=invoice)
    if request.method == "POST" and form.is_valid() and formset.is_valid():
        invoice = form.save(commit=False)
        invoice.save()
        formset.instance = invoice
        formset.save()
        invoice.recalculate()
        invoice.save(update_fields=["subtotal", "tax_amount", "grand_total", "status", "updated_at"])
        logger.info("Invoice created | invoice=%s | user=%s | total=%s", invoice.invoice_number, request.user.username, invoice.grand_total)
        messages.success(request, "Invoice created successfully.")
        return redirect("invoice_detail", pk=invoice.pk)
    product_values = {
        str(product.pk): {"unit_price": str(product.selling_price), "gst_rate": str(product.gst_rate)}
        for product in Product.objects.filter(is_active=True).only("id", "selling_price", "gst_rate")
    }
    return render(request, "invoices/form.html", {"form": form, "formset": formset, "title": "Create Invoice", "product_values": json.dumps(product_values)})

@login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice.objects.select_related("customer").prefetch_related("items__product"), pk=pk)
    return render(request, "invoices/detail.html", {"invoice": invoice})

@login_required
def invoice_pdf(request, pk):
    invoice = get_object_or_404(Invoice.objects.select_related("customer").prefetch_related("items__product"), pk=pk)
    logger.info("Invoice PDF generated | invoice=%s | user=%s", invoice.invoice_number, request.user.username)
    return FileResponse(
        build_invoice_pdf(invoice, company=CompanyProfile.get_default()),
        as_attachment=True,
        filename=f"{invoice.invoice_number}.pdf",
    )
