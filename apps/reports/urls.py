from django.urls import path
from .views import collection_report, sales_csv, sales_report

urlpatterns = [
    path("sales/", sales_report, name="sales_report"),
    path("sales.csv", sales_csv, name="sales_csv"),
    path("collections/", collection_report, name="collection_report"),
]
