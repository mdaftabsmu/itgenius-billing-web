from django import forms
from django.forms import inlineformset_factory
from .models import Quotation, QuotationItem


class QuotationForm(forms.ModelForm):
    class Meta:
        model = Quotation
        fields = ["customer", "valid_until", "discount_amount", "notes", "terms", "status"]
        widgets = {"valid_until": forms.DateInput(attrs={"type": "date"}), "notes": forms.Textarea(attrs={"rows": 3}), "terms": forms.Textarea(attrs={"rows": 3})}


class QuotationItemForm(forms.ModelForm):
    class Meta:
        model = QuotationItem
        fields = ["product", "description", "quantity", "unit_price", "gst_rate"]


QuotationItemFormSet = inlineformset_factory(Quotation, QuotationItem, form=QuotationItemForm, extra=1, can_delete=True)
