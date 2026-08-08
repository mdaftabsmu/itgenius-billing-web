from django.db import models


class Customer(models.Model):
    customer_code = models.CharField(max_length=30, unique=True, db_index=True)
    name = models.CharField(max_length=150)
    company_name = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=15, blank=True)
    gst_number = models.CharField(max_length=20, blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["name"]), models.Index(fields=["phone"]), models.Index(fields=["gst_number"])]

    def __str__(self):
        return f"{self.customer_code} - {self.name}"
