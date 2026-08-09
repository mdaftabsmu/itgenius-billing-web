from django.db import migrations, models
import django.core.validators
import decimal
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [("categories", "0001_initial")]
    operations = [migrations.CreateModel(name="Product", fields=[
        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
        ("product_code", models.CharField(db_index=True, max_length=50, unique=True)), ("name", models.CharField(max_length=200)),
        ("description", models.TextField(blank=True)), ("unit", models.CharField(default="PCS", max_length=30)),
        ("purchase_price", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=12, validators=[django.core.validators.MinValueValidator(decimal.Decimal("0"))])),
        ("selling_price", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=12, validators=[django.core.validators.MinValueValidator(decimal.Decimal("0"))])),
        ("gst_rate", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=5, validators=[django.core.validators.MinValueValidator(decimal.Decimal("0"))])),
        ("stock_quantity", models.DecimalField(decimal_places=3, default=decimal.Decimal("0.000"), max_digits=14, validators=[django.core.validators.MinValueValidator(decimal.Decimal("0"))])),
        ("low_stock_threshold", models.DecimalField(decimal_places=3, default=decimal.Decimal("5.000"), max_digits=14, validators=[django.core.validators.MinValueValidator(decimal.Decimal("0"))])),
        ("barcode", models.CharField(blank=True, db_index=True, max_length=100)), ("is_active", models.BooleanField(default=True)),
        ("created_at", models.DateTimeField(auto_now_add=True)), ("updated_at", models.DateTimeField(auto_now=True)),
        ("category", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="products", to="categories.category")),
    ], options={"ordering": ["name"], "indexes": [models.Index(fields=["name"], name="products_pro_name_6a8d7d_idx"), models.Index(fields=["category", "is_active"], name="products_pro_categor_5d5c43_idx")]})]
