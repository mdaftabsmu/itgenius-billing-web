from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.customers.models import Customer
from apps.products.models import Product
from apps.invoices.models import Invoice
from .serializers import CustomerSerializer, ProductSerializer, InvoiceSerializer

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["is_active", "city", "state"]
    search_fields = ["customer_code", "name", "company_name", "phone", "gst_number"]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["is_active"]
    search_fields = ["code", "name"]

class InvoiceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Invoice.objects.select_related("customer").all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["status", "customer"]
    search_fields = ["invoice_number", "customer__name"]
