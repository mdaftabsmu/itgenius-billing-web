from decimal import Decimal
import pytest
from apps.categories.models import Category
from apps.customers.models import Customer
from apps.products.models import Product
from apps.invoices.models import Invoice, InvoiceItem

@pytest.mark.django_db
def test_invoice_recalculate_totals():
    category = Category.objects.create(name="Test")
    customer = Customer.objects.create(customer_code="CUST-TEST", name="Test Customer")
    product = Product.objects.create(product_code="PROD-TEST", name="Test Product", category=category, selling_price=Decimal("100.00"))
    invoice = Invoice.objects.create(invoice_number="INV-TEST", customer=customer, discount_amount=Decimal("10.00"))
    InvoiceItem.objects.create(invoice=invoice, product=product, quantity=Decimal("2"), unit_price=Decimal("100.00"), gst_rate=Decimal("18"))
    invoice.recalculate()
    assert invoice.subtotal == Decimal("200.00")
    assert invoice.tax_amount == Decimal("36.00")
    assert invoice.grand_total == Decimal("226.00")
    assert invoice.balance_due == Decimal("226.00")
