from decimal import Decimal
from django.core.validators import MinValueValidator
from django.db import models
from apps.categories.models import Category

class Product(models.Model):
    product_code = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    description = models.TextField(blank=True)
    unit = models.CharField(max_length=30, default="PCS")
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"), validators=[MinValueValidator(Decimal("0"))])
    selling_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"), validators=[MinValueValidator(Decimal("0"))])
    gst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"), validators=[MinValueValidator(Decimal("0"))])
    stock_quantity = models.DecimalField(max_digits=14, decimal_places=3, default=Decimal("0.000"), validators=[MinValueValidator(Decimal("0"))])
    low_stock_threshold = models.DecimalField(max_digits=14, decimal_places=3, default=Decimal("5.000"), validators=[MinValueValidator(Decimal("0"))])
    barcode = models.CharField(max_length=100, blank=True, db_index=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["name"]), models.Index(fields=["category", "is_active"])]

    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.low_stock_threshold

    def __str__(self):
        return f"{self.product_code} - {self.name}"
