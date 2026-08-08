from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("product_code", "name", "category", "selling_price", "gst_rate", "stock_quantity", "is_active")
    search_fields = ("product_code", "name", "barcode")
    list_filter = ("category", "is_active")
