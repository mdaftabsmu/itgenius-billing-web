from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["product_code", "name", "category", "description", "unit", "purchase_price", "selling_price", "gst_rate", "stock_quantity", "low_stock_threshold", "barcode", "is_active"]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}
