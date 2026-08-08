from django.contrib import admin
from .models import CompanyProfile

@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Company", {"fields": ("name", "tagline", "logo", "address", "phone", "email", "website", "gst_number", "pan_number")}),
        ("Numbering", {"fields": ("quotation_prefix", "invoice_prefix")}),
        ("Documents", {"fields": ("quotation_terms", "invoice_terms")}),
    )

    def has_add_permission(self, request):
        return not CompanyProfile.objects.exists()
