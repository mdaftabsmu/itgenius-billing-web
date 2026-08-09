from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [migrations.CreateModel(name="Customer", fields=[
        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
        ("customer_code", models.CharField(db_index=True, max_length=30, unique=True)),
        ("name", models.CharField(max_length=150)), ("company_name", models.CharField(blank=True, max_length=200)),
        ("phone", models.CharField(blank=True, max_length=30)), ("email", models.EmailField(blank=True, max_length=254)),
        ("address", models.TextField(blank=True)), ("city", models.CharField(blank=True, max_length=100)),
        ("state", models.CharField(blank=True, max_length=100)), ("pincode", models.CharField(blank=True, max_length=15)),
        ("gst_number", models.CharField(blank=True, max_length=20)), ("notes", models.TextField(blank=True)),
        ("is_active", models.BooleanField(default=True)), ("created_at", models.DateTimeField(auto_now_add=True)),
        ("updated_at", models.DateTimeField(auto_now=True)),
    ], options={"ordering": ["name"], "indexes": [models.Index(fields=["name"], name="customers_cust_name_4d3f12_idx"), models.Index(fields=["phone"], name="customers_cust_phone_0a9c0d_idx"), models.Index(fields=["gst_number"], name="customers_cust_gst_nu_1a4f4d_idx")]})]
