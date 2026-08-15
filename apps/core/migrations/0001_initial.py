from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="CompanyProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(default="ITGenius Computer", max_length=200)),
                ("tagline", models.CharField(blank=True, max_length=250)),
                ("address", models.TextField(blank=True)),
                ("phone", models.CharField(blank=True, max_length=50)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("website", models.URLField(blank=True)),
                ("gst_number", models.CharField(blank=True, max_length=30)),
                ("pan_number", models.CharField(blank=True, max_length=20)),
                ("logo", models.ImageField(blank=True, null=True, upload_to="company/")),
                ("quotation_prefix", models.CharField(default="QT", max_length=10)),
                ("invoice_prefix", models.CharField(default="INV", max_length=10)),
                ("quotation_terms", models.TextField(blank=True)),
                ("invoice_terms", models.TextField(blank=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
