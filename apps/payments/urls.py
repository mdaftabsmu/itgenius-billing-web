from django.urls import path
from .views import payment_create, payment_list

urlpatterns = [
    path("", payment_list, name="payment_list"),
    path("new/", payment_create, name="payment_create"),
]
