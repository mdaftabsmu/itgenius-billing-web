import logging
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from .forms import QuotationForm, QuotationItemFormSet
from .models import Quotation

logger = logging.getLogger("billing")


def _next_number():
    prefix = "QT"
    last = Quotation.objects.order_by("-id").first()
    return f"{prefix}-{last.id + 1:06d}" if last else f"{prefix}-000001"


@login_required
def quotation_list(request):
    quotations = Quotation.objects.select_related("customer").all()
    return render(request, "quotations/list.html", {"quotations": quotations})


@login_required
@transaction.atomic
def quotation_create(request):
    quotation = Quotation(quotation_number=_next_number())
    form = QuotationForm(request.POST or None, instance=quotation)
    formset = QuotationItemFormSet(request.POST or None, instance=quotation)
    if request.method == "POST" and form.is_valid() and formset.is_valid():
        quotation = form.save(commit=False)
        quotation.save()
        formset.instance = quotation
        formset.save()
        quotation.recalculate()
        quotation.save(update_fields=["subtotal", "tax_amount", "grand_total", "updated_at"])
        logger.info("Quotation created | quotation=%s | user=%s | total=%s", quotation.quotation_number, request.user.username, quotation.grand_total)
        messages.success(request, "Quotation created successfully.")
        return redirect("quotation_list")
    return render(request, "quotations/form.html", {"form": form, "formset": formset, "title": "Create Quotation"})


@login_required
def quotation_detail(request, pk):
    quotation = get_object_or_404(Quotation.objects.select_related("customer").prefetch_related("items__product"), pk=pk)
    return render(request, "quotations/detail.html", {"quotation": quotation})
