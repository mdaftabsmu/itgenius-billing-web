import logging
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from .forms import CategoryForm
from .models import Category

logger = logging.getLogger("billing")

@login_required
def category_list(request):
    categories = Category.objects.filter(is_active=True)
    return render(request, "categories/list.html", {"categories": categories})

@login_required
def category_create(request):
    form = CategoryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        category = form.save()
        logger.info("Category created | category_id=%s | user=%s", category.pk, request.user.username)
        messages.success(request, "Category created successfully.")
        return redirect("category_list")
    return render(request, "categories/form.html", {"form": form, "title": "Add Category"})

@login_required
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, instance=category)
    if request.method == "POST" and form.is_valid():
        form.save()
        logger.info("Category updated | category_id=%s | user=%s", pk, request.user.username)
        messages.success(request, "Category updated successfully.")
        return redirect("category_list")
    return render(request, "categories/form.html", {"form": form, "title": "Edit Category"})
