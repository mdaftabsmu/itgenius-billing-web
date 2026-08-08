from django.urls import path
from .views import quotation_create, quotation_detail, quotation_list

urlpatterns = [
    path("", quotation_list, name="quotation_list"),
    path("new/", quotation_create, name="quotation_create"),
    path("<int:pk>/", quotation_detail, name="quotation_detail"),
]
