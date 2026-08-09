from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

class Command(BaseCommand):
    help = "Create standard ITGenius Billing roles"
    roles = {
        "Administrator": None,
        "Manager": ["view_quotation", "add_quotation", "change_quotation", "view_invoice", "add_invoice", "change_invoice", "view_payment", "add_payment"],
        "Sales": ["view_customer", "add_customer", "change_customer", "view_product", "view_quotation", "add_quotation", "change_quotation", "view_invoice", "add_invoice"],
        "Accountant": ["view_invoice", "add_invoice", "change_invoice", "view_payment", "add_payment", "view_quotation"],
        "Viewer": ["view_customer", "view_product", "view_quotation", "view_invoice", "view_payment"],
    }
    def handle(self, *args, **kwargs):
        for role, codenames in self.roles.items():
            group, _ = Group.objects.get_or_create(name=role)
            if role == "Administrator":
                group.permissions.set(Permission.objects.all())
            else:
                group.permissions.set(Permission.objects.filter(codename__in=codenames))
            self.stdout.write(self.style.SUCCESS(f"Configured role: {role}"))
