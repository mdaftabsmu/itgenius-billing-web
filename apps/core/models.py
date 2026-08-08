from django.db import models

class CompanyProfile(models.Model):
    name = models.CharField(max_length=200, default="ITGenius Computer")
    tagline = models.CharField(max_length=250, blank=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    gst_number = models.CharField(max_length=30, blank=True)
    pan_number = models.CharField(max_length=20, blank=True)
    logo = models.ImageField(upload_to="company/", blank=True, null=True)
    quotation_prefix = models.CharField(max_length=10, default="QT")
    invoice_prefix = models.CharField(max_length=10, default="INV")
    quotation_terms = models.TextField(blank=True)
    invoice_terms = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @classmethod
    def get_default(cls):
        profile, _ = cls.objects.get_or_create(pk=1)
        return profile
