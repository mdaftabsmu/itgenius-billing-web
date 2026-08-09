from django.db.models import Sum
from apps.invoices.models import Invoice
from apps.payments.models import Payment

def sales_summary():
    result = Invoice.objects.aggregate(subtotal=Sum("subtotal"), tax=Sum("tax_amount"), total=Sum("grand_total"), paid=Sum("paid_amount"))
    result = {key: value or 0 for key, value in result.items()}
    result["outstanding"] = result["total"] - result["paid"]
    return result

def collection_summary():
    result = Payment.objects.aggregate(total=Sum("amount"))
    return {"total": result["total"] or 0}
