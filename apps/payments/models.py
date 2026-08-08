from decimal import Decimal
from django.core.validators import MinValueValidator
from django.db import models
from apps.invoices.models import Invoice

class Payment(models.Model):
    METHOD_CHOICES = [("CASH", "Cash"), ("UPI", "UPI"), ("CARD", "Card"), ("BANK", "Bank Transfer"), ("CHEQUE", "Cheque"), ("OTHER", "Other")]
    payment_number = models.CharField(max_length=40, unique=True, db_index=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, related_name="payments")
    payment_date = models.DateField(auto_now_add=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default="CASH")
    reference_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.payment_number
