from django.contrib import admin
from .models import Quotation, QuotationItem

class QuotationItemInline(admin.TabularInline):
    model = QuotationItem
    extra = 0

@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = ("quotation_number", "customer", "quotation_date", "grand_total", "status")
    search_fields = ("quotation_number", "customer__name", "customer__company_name")
    list_filter = ("status", "quotation_date")
    inlines = [QuotationItemInline]
