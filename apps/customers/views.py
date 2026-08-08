import logging
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import ModelSerializer
from .forms import CustomerForm
from .models import Customer

logger = logging.getLogger("billing")


@login_required
def customer_list(request):
    query = request.GET.get("q", "").strip()
    customers = Customer.objects.filter(is_active=True)
    if query:
        customers = customers.filter(Q(name__icontains=query) | Q(company_name__icontains=query) | Q(phone__icontains=query) | Q(customer_code__icontains=query))
    paginator = Paginator(customers, 20)
    page = paginator.get_page(request.GET.get("page"))
    return render(request, "customers/list.html", {"page": page, "query": query})


@login_required
def customer_create(request):
    form = CustomerForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        customer = form.save()
        logger.info("Customer created | customer_id=%s | user=%s", customer.pk, request.user.username)
        messages.success(request, "Customer created successfully.")
        return redirect("customer_list")
    return render(request, "customers/form.html", {"form": form, "title": "Add Customer"})


@login_required
def customer_update(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    form = CustomerForm(request.POST or None, instance=customer)
    if request.method == "POST" and form.is_valid():
        form.save()
        logger.info("Customer updated | customer_id=%s | user=%s", pk, request.user.username)
        messages.success(request, "Customer updated successfully.")
        return redirect("customer_list")
    return render(request, "customers/form.html", {"form": form, "title": "Edit Customer"})


@login_required
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == "POST":
        customer.is_active = False
        customer.save(update_fields=["is_active", "updated_at"])
        logger.info("Customer deactivated | customer_id=%s | user=%s", pk, request.user.username)
        messages.success(request, "Customer removed successfully.")
    return redirect("customer_list")


class CustomerSerializer(ModelSerializer):
    class Meta:
        model = Customer
        fields = "__all__"


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
