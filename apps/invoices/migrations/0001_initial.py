from django.db import migrations, models
import decimal
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [("customers", "0001_initial"), ("products", "0001_initial")]
    operations = [
        migrations.CreateModel(name="Invoice", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("invoice_number", models.CharField(db_index=True, max_length=40, unique=True)),
            ("invoice_date", models.DateField(auto_now_add=True)), ("due_date", models.DateField(blank=True, null=True)),
            ("subtotal", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=12)), ("discount_amount", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=12)),
            ("tax_amount", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=12)), ("grand_total", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=12)),
            ("paid_amount", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=12)), ("notes", models.TextField(blank=True)), ("terms", models.TextField(blank=True)),
            ("status", models.CharField(choices=[("DRAFT", "Draft"), ("ISSUED", "Issued"), ("PARTIAL", "Partially Paid"), ("PAID", "Paid"), ("CANCELLED", "Cancelled")], default="DRAFT", max_length=20)),
            ("created_at", models.DateTimeField(auto_now_add=True)), ("updated_at", models.DateTimeField(auto_now=True)),
            ("customer", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="invoices", to="customers.customer")),
        ]),
        migrations.CreateModel(name="InvoiceItem", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("description", models.CharField(blank=True, max_length=300)),
            ("quantity", models.DecimalField(decimal_places=3, max_digits=12)), ("unit_price", models.DecimalField(decimal_places=2, max_digits=12)), ("gst_rate", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=5)),
            ("amount", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=12)), ("tax_amount", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=12)),
            ("invoice", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="invoices.invoice")), ("product", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="products.product")),
        ])]
