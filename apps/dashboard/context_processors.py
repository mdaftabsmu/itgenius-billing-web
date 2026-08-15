from django.urls import reverse


def sidebar(request):
    """Provide the authenticated application navigation to every template."""
    if not request.user.is_authenticated:
        return {}

    view_name = getattr(request.resolver_match, "url_name", "")
    active_sidebar_item = {
        "dashboard": "dashboard",
        "customer_list": "customers",
        "customer_create": "customers",
        "customer_update": "customers",
        "customer_delete": "customers",
        "category_list": "categories",
        "category_create": "categories",
        "category_update": "categories",
        "product_list": "products",
        "product_create": "products",
        "product_update": "products",
        "quotation_list": "quotations",
        "quotation_create": "quotations",
        "quotation_detail": "quotations",
        "invoice_list": "invoices",
        "invoice_create": "invoices",
        "invoice_detail": "invoices",
        "invoice_pdf": "invoices",
        "payment_list": "payments",
        "payment_create": "payments",
        "sales_report": "reports",
        "collection_report": "reports",
    }.get(view_name)

    return {
        "active_sidebar_item": active_sidebar_item,
        "sidebar_items": [
            {"label": "Dashboard", "url": reverse("dashboard"), "key": "dashboard"},
            {"label": "Customers", "url": reverse("customer_list"), "key": "customers"},
            {"label": "Categories", "url": reverse("category_list"), "key": "categories"},
            {"label": "Products", "url": reverse("product_list"), "key": "products"},
            {"label": "Quotations", "url": reverse("quotation_list"), "key": "quotations"},
            {"label": "Invoices", "url": reverse("invoice_list"), "key": "invoices"},
            {"label": "Payments", "url": reverse("payment_list"), "key": "payments"},
            {"label": "Reports", "url": reverse("sales_report"), "key": "reports"},
        ],
    }
