from rest_framework import serializers
from apps.customers.models import Customer
from apps.products.models import Product
from apps.invoices.models import Invoice

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = "__all__"

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"

class InvoiceSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    balance_due = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    class Meta:
        model = Invoice
        fields = ["id", "invoice_number", "customer", "customer_name", "invoice_date", "due_date", "subtotal", "discount_amount", "tax_amount", "grand_total", "paid_amount", "balance_due", "status", "notes", "terms"]
