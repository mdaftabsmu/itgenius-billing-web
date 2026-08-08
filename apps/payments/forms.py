from django import forms
from .models import Payment

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["invoice", "amount", "method", "reference_number", "notes"]
        widgets = {"notes": forms.Textarea(attrs={"rows": 3})}
