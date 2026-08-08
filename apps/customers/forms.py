from django import forms
from .models import Customer


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            "customer_code", "name", "company_name", "phone", "email",
            "address", "city", "state", "pincode", "gst_number", "notes", "is_active",
        ]
        widgets = {"address": forms.Textarea(attrs={"rows": 3}), "notes": forms.Textarea(attrs={"rows": 3})}
