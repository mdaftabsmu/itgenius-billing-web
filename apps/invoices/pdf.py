from apps.core.pdf import invoice_pdf


def build_invoice_pdf(invoice, company=None):
    """Build an invoice PDF using the branded billing-document layout."""
    return invoice_pdf(invoice, company=company)
