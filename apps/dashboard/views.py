import logging
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.shortcuts import render
from apps.customers.models import Customer
from apps.products.models import Product
from apps.quotations.models import Quotation
from apps.invoices.models import Invoice
from apps.payments.models import Payment

logger = logging.getLogger("billing")

@login_required
def dashboard(request):
    invoice_totals = Invoice.objects.aggregate(total=Sum("grand_total"), paid=Sum("paid_amount"))
    context = {
        "customer_count": Customer.objects.count(),
        "product_count": Product.objects.filter(is_active=True).count(),
        "quotation_count": Quotation.objects.count(),
        "invoice_count": Invoice.objects.count(),
        "payment_count": Payment.objects.count(),
        "sales_total": invoice_totals["total"] or Decimal("0.00"),
        "collection_total": invoice_totals["paid"] or Decimal("0.00"),
        "outstanding_total": (invoice_totals["total"] or Decimal("0.00")) - (invoice_totals["paid"] or Decimal("0.00")),
        "recent_invoices": Invoice.objects.select_related("customer").order_by("-invoice_date", "-id")[:10],
        "low_stock_products": Product.objects.filter(is_active=True, stock_quantity__lte=models.F("low_stock_threshold"))[:10],
    }
    logger.info("Dashboard viewed | user=%s", request.user.username)
    return render(request, "dashboard/index.html", context)
