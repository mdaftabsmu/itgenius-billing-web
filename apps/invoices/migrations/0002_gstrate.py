from decimal import Decimal

from django.db import migrations, models


def add_default_gst_rates(apps, schema_editor):
    GSTRate = apps.get_model("invoices", "GSTRate")
    for rate in ("0.00", "5.00", "12.00", "18.00", "28.00"):
        GSTRate.objects.get_or_create(rate=Decimal(rate))


class Migration(migrations.Migration):
    dependencies = [("invoices", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="GSTRate",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("rate", models.DecimalField(decimal_places=2, max_digits=5, unique=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"ordering": ["rate"]},
        ),
        migrations.RunPython(add_default_gst_rates, migrations.RunPython.noop),
    ]
