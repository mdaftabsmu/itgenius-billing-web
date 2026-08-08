from django.urls import path
from .views import category_create, category_list, category_update

urlpatterns = [
    path("", category_list, name="category_list"),
    path("new/", category_create, name="category_create"),
    path("<int:pk>/edit/", category_update, name="category_update"),
]
