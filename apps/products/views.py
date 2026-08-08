import logging
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from .forms import ProductForm
from .models import Product

logger = logging.getLogger("billing")

@login_required
def product_list(request):
    query = request.GET.get("q", "").strip()
    products = Product.objects.select_related("category").filter(is_active=True)
    if query:
        products = products.filter(Q(name__icontains=query) | Q(product_code__icontains=query) | Q(barcode__icontains=query))
    page = Paginator(products, 20).get_page(request.GET.get("page"))
    return render(request, "products/list.html", {"page": page, "query": query})

@login_required
def product_create(request):
    form = ProductForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        product = form.save()
        logger.info("Product created | product_id=%s | user=%s", product.pk, request.user.username)
        messages.success(request, "Product created successfully.")
        return redirect("product_list")
    return render(request, "products/form.html", {"form": form, "title": "Add Product"})

@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, instance=product)
    if request.method == "POST" and form.is_valid():
        form.save()
        logger.info("Product updated | product_id=%s | user=%s", pk, request.user.username)
        messages.success(request, "Product updated successfully.")
        return redirect("product_list")
    return render(request, "products/form.html", {"form": form, "title": "Edit Product"})
