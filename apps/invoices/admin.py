from django.contrib import admin
from .models import GSTRate, Invoice, InvoiceItem


@admin.register(GSTRate)
class GSTRateAdmin(admin.ModelAdmin):
    list_display = ("rate", "is_active")
    list_editable = ("is_active",)

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("invoice_number", "customer", "invoice_date", "grand_total", "paid_amount", "status")
    search_fields = ("invoice_number", "customer__name", "customer__company_name")
    list_filter = ("status", "invoice_date")
    inlines = [InvoiceItemInline]
