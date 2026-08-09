from django.db import migrations, models
import decimal
import django.db.models.deletion
import django.core.validators

class Migration(migrations.Migration):
    initial = True
    dependencies = [("invoices", "0001_initial")]
    operations = [migrations.CreateModel(name="Payment", fields=[
        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
        ("payment_number", models.CharField(db_index=True, max_length=40, unique=True)), ("payment_date", models.DateField(auto_now_add=True)),
        ("amount", models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(decimal.Decimal("0.01"))])),
        ("method", models.CharField(choices=[("CASH", "Cash"), ("UPI", "UPI"), ("CARD", "Card"), ("BANK", "Bank Transfer"), ("CHEQUE", "Cheque"), ("OTHER", "Other")], default="CASH", max_length=20)),
        ("reference_number", models.CharField(blank=True, max_length=100)), ("notes", models.TextField(blank=True)), ("created_at", models.DateTimeField(auto_now_add=True)),
        ("invoice", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="payments", to="invoices.invoice")),
    ])]
