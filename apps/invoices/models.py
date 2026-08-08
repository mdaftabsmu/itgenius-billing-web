from decimal import Decimal
from django.db import models
from apps.customers.models import Customer
from apps.products.models import Product

class Invoice(models.Model):
    invoice_number = models.CharField(max_length=40, unique=True, db_index=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="invoices")
    invoice_date = models.DateField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    notes = models.TextField(blank=True)
    terms = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=[("DRAFT", "Draft"), ("ISSUED", "Issued"), ("PARTIAL", "Partially Paid"), ("PAID", "Paid"), ("CANCELLED", "Cancelled")], default="DRAFT")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def balance_due(self):
        return max(self.grand_total - self.paid_amount, Decimal("0.00"))

    def recalculate(self):
        self.subtotal = sum((item.amount for item in self.items.all()), Decimal("0.00"))
        self.tax_amount = sum((item.tax_amount for item in self.items.all()), Decimal("0.00"))
        self.grand_total = self.subtotal - self.discount_amount + self.tax_amount
        if self.paid_amount >= self.grand_total and self.grand_total > 0:
            self.status = "PAID"
        elif self.paid_amount > 0:
            self.status = "PARTIAL"

    def __str__(self):
        return self.invoice_number

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    description = models.CharField(max_length=300, blank=True)
    quantity = models.DecimalField(max_digits=12, decimal_places=3)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    gst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    def save(self, *args, **kwargs):
        self.amount = self.quantity * self.unit_price
        self.tax_amount = self.amount * self.gst_rate / Decimal("100")
        super().save(*args, **kwargs)
