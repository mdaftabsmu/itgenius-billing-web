from decimal import Decimal
import pytest
from apps.categories.models import Category
from apps.customers.models import Customer
from apps.products.models import Product
from apps.invoices.models import Invoice, InvoiceItem
from apps.payments.models import Payment

@pytest.mark.django_db
def test_payment_updates_invoice_paid_amount():
    category = Category.objects.create(name="Payment Test")
    customer = Customer.objects.create(customer_code="CUST-PAY", name="Payment Customer")
    product = Product.objects.create(product_code="PROD-PAY", name="Payment Product", category=category, selling_price=Decimal("100.00"))
    invoice = Invoice.objects.create(invoice_number="INV-PAY", customer=customer)
    InvoiceItem.objects.create(invoice=invoice, product=product, quantity=1, unit_price=Decimal("100.00"), gst_rate=Decimal("0"))
    invoice.recalculate(); invoice.save()
    payment = Payment.objects.create(payment_number="PAY-TEST", invoice=invoice, amount=Decimal("40.00"), method="UPI")
    invoice.paid_amount += payment.amount
    invoice.recalculate(); invoice.save()
    assert invoice.paid_amount == Decimal("40.00")
    assert invoice.balance_due == Decimal("60.00")
    assert invoice.status == "PARTIAL"
