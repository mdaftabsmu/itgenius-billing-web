from django.db import migrations, models
import decimal
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [("customers", "0001_initial"), ("products", "0001_initial")]
    operations = [
        migrations.CreateModel(name="Quotation", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("quotation_number", models.CharField(db_index=True, max_length=40, unique=True)), ("quotation_date", models.DateField(auto_now_add=True)),
            ("valid_until", models.DateField(blank=True, null=True)), ("discount_amount", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=12)),
            ("tax_amount", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=12)), ("subtotal", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=12)),
            ("grand_total", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=12)), ("notes", models.TextField(blank=True)), ("terms", models.TextField(blank=True)),
            ("status", models.CharField(choices=[("DRAFT", "Draft"), ("SENT", "Sent"), ("ACCEPTED", "Accepted"), ("REJECTED", "Rejected"), ("EXPIRED", "Expired")], default="DRAFT", max_length=20)),
            ("created_at", models.DateTimeField(auto_now_add=True)), ("updated_at", models.DateTimeField(auto_now=True)),
            ("customer", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="quotations", to="customers.customer")),
        ], options={"ordering": ["-created_at"]}),
        migrations.CreateModel(name="QuotationItem", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("description", models.CharField(blank=True, max_length=300)),
            ("quantity", models.DecimalField(decimal_places=3, max_digits=12)), ("unit_price", models.DecimalField(decimal_places=2, max_digits=12)),
            ("gst_rate", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=5)), ("amount", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=12)),
            ("tax_amount", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=12)),
            ("product", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="products.product")),
            ("quotation", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="quotations.quotation")),
        ])]
