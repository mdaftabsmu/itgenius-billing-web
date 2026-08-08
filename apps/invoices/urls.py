from django.urls import path
from .views import invoice_create, invoice_detail, invoice_list, invoice_pdf

urlpatterns = [
    path("", invoice_list, name="invoice_list"),
    path("new/", invoice_create, name="invoice_create"),
    path("<int:pk>/", invoice_detail, name="invoice_detail"),
    path("<int:pk>/pdf/", invoice_pdf, name="invoice_pdf"),
]
