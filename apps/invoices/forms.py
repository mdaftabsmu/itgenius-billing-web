from django import forms
from django.forms import inlineformset_factory
from .models import GSTRate, Invoice, InvoiceItem

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ["customer", "due_date", "discount_amount", "notes", "terms", "status"]
        widgets = {"due_date": forms.DateInput(attrs={"type": "date"}), "notes": forms.Textarea(attrs={"rows": 3}), "terms": forms.Textarea(attrs={"rows": 3})}

class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ["product", "description", "quantity", "unit_price", "gst_rate"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        rates = GSTRate.objects.filter(is_active=True)
        self.fields["gst_rate"] = forms.TypedChoiceField(
            choices=[(rate.rate, f"{rate.rate:g}%") for rate in rates],
            coerce=Decimal,
        )
        self.fields["quantity"].widget.attrs.update({"class": "form-control js-quantity", "min": "0", "step": "0.001"})
        self.fields["unit_price"].widget.attrs.update({"class": "form-control js-unit-price", "min": "0", "step": "0.01"})
        self.fields["gst_rate"].widget.attrs.update({"class": "form-select js-gst-rate"})

InvoiceItemFormSet = inlineformset_factory(Invoice, InvoiceItem, form=InvoiceItemForm, extra=1, can_delete=True)
