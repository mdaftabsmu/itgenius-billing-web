from decimal import Decimal, InvalidOperation
from io import BytesIO
from pathlib import Path
import re

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from .models import CompanyProfile

PAGE_W, PAGE_H = A4
BLUE = colors.HexColor("#2F69B5")
DARK_BLUE = colors.HexColor("#2A5F9E")
ORANGE = colors.HexColor("#E8942E")
ROW_GREY = colors.HexColor("#F1F1F1")
YELLOW = colors.HexColor("#FFD43B")
TEXT = colors.HexColor("#202020")
BORDER = colors.HexColor("#2F69B5")
GRID = colors.HexColor("#2F69B5")
DEFAULT_LOGO_PATH = Path(__file__).resolve().parents[2] / "static" / "images" / "itgenius-computer-logo.jpg"

FONT = "Helvetica"
FONT_BOLD = "Helvetica-Bold"
FONT_ITALIC = "Helvetica-Oblique"


def _register_fonts():
    global FONT, FONT_BOLD, FONT_ITALIC
    locations = [
        Path(__file__).resolve().parent / "fonts",
        Path("/usr/share/fonts/truetype/dejavu"),
    ]
    for folder in locations:
        regular = folder / "DejaVuSans.ttf"
        bold = folder / "DejaVuSans-Bold.ttf"
        italic = folder / "DejaVuSans-Oblique.ttf"
        if regular.exists() and bold.exists():
            try:
                pdfmetrics.registerFont(TTFont("ITGeniusSans", str(regular)))
                pdfmetrics.registerFont(TTFont("ITGeniusSansBold", str(bold)))
                if italic.exists():
                    pdfmetrics.registerFont(TTFont("ITGeniusSansItalic", str(italic)))
                FONT = "ITGeniusSans"
                FONT_BOLD = "ITGeniusSansBold"
                FONT_ITALIC = "ITGeniusSansItalic" if italic.exists() else FONT
                return
            except Exception:
                pass


_register_fonts()


def _decimal(value):
    try:
        return Decimal(str(value or 0))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal("0.00")


def _money(value):
    return f"₹ {_decimal(value):,.2f}"


def _date(value):
    if not value:
        return "-"
    try:
        return value.strftime("%d-%m-%Y")
    except AttributeError:
        value = str(value)
        if len(value) >= 10 and value[4] == "-" and value[7] == "-":
            return f"{value[8:10]}-{value[5:7]}-{value[:4]}"
        return value


def _logo_path(company):
    """Use the bundled ITGenius logo; fall back to an uploaded company logo."""
    if DEFAULT_LOGO_PATH.exists():
        return DEFAULT_LOGO_PATH
    logo = getattr(company, "logo", None)
    if logo:
        try:
            path = Path(logo.path)
            if path.exists():
                return path
        except (AttributeError, OSError, ValueError):
            pass
    return None


def _draw_wrapped(c, text, x, y, max_width, size=8, leading=10, font=None, max_lines=3):
    text = str(text or "").replace("\n", " ").strip()
    if not text:
        return y
    font = font or FONT
    c.setFont(font, size)
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if not current or c.stringWidth(candidate, font, size) <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    for line in lines[:max_lines]:
        c.drawString(x, y, line)
        y -= leading
    return y


def _section(c, title, x, top, width, height=18):
    c.setFillColor(BLUE)
    c.rect(x, top - height, width, height, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont(FONT_BOLD, 9)
    c.drawString(x + 5, top - height + 5, title)


def _draw_detail_icon(c, kind, x, y):
    """Draw small print-safe contact icons without depending on a web font."""
    c.saveState()
    c.setStrokeColor(DARK_BLUE)
    c.setFillColor(DARK_BLUE)
    c.setLineWidth(1)
    if kind == "location":
        c.circle(x + 3, y + 2, 2.4, fill=0, stroke=1)
        c.line(x + 3, y - 4, x + 1, y)
        c.line(x + 3, y - 4, x + 5, y)
    elif kind == "web":
        c.circle(x + 3, y, 3.4, fill=0, stroke=1)
        c.line(x, y, x + 6, y)
        c.line(x + 3, y - 3.4, x + 3, y + 3.4)
    elif kind == "phone":
        c.setLineWidth(1.7)
        c.line(x + 1, y + 3, x + 5, y - 2)
        c.circle(x + 1, y + 3, 0.9, fill=1, stroke=0)
        c.circle(x + 5, y - 2, 0.9, fill=1, stroke=0)
    elif kind == "email":
        c.rect(x, y - 2.5, 7, 5, fill=0, stroke=1)
        c.line(x, y + 2.5, x + 3.5, y - 0.5)
        c.line(x + 7, y + 2.5, x + 3.5, y - 0.5)
    elif kind == "building":
        c.rect(x + 1, y - 3, 5, 7, fill=0, stroke=1)
        for offset in (2, 4):
            c.line(x + offset, y + 2, x + offset, y + 3)
            c.line(x + offset, y - 1, x + offset, y)
    else:  # contact/person
        c.circle(x + 3.5, y + 2, 1.6, fill=1, stroke=0)
        c.roundRect(x + 1, y - 3, 5, 3.5, 1, fill=1, stroke=0)
    c.restoreState()


def _draw_contact_line(c, kind, text, x, y, width, size=7.5, max_lines=1):
    _draw_detail_icon(c, kind, x, y - 2)
    return _draw_wrapped(c, text, x + 11, y, width - 11, size=size, leading=9, max_lines=max_lines)


def _format_address(value):
    """Make customer-entered comma-separated addresses readable in narrow PDF blocks."""
    return re.sub(r",\s*", ", ", str(value or "").strip())


def _metadata(c, document, document_type, x, top, width=92 * mm):
    row_h = 18
    label_w = 42 * mm
    value_w = width - label_w
    is_invoice = document_type == "INVOICE"
    rows = [
        ("DATE", _date(getattr(document, "invoice_date" if is_invoice else "quotation_date", None))),
        ("INVOICE #" if is_invoice else "QUOTE #", str(getattr(document, "invoice_number" if is_invoice else "quotation_number", "-"))),
        ("CUSTOMER ID", str(getattr(document.customer, "customer_code", "-"))),
        ("DUE DATE" if is_invoice else "VALID UNTIL", _date(getattr(document, "due_date" if is_invoice else "valid_until", None))),
    ]
    for i, (label, value) in enumerate(rows):
        y = top - i * row_h
        c.setFillColor(colors.HexColor("#F6F6F6"))
        c.rect(x, y - row_h, label_w, row_h, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.rect(x + label_w, y - row_h, value_w, row_h, fill=1, stroke=0)
        c.setStrokeColor(colors.HexColor("#999999"))
        c.setLineWidth(0.45)
        c.rect(x, y - row_h, width, row_h, fill=0, stroke=1)
        c.line(x + label_w, y - row_h, x + label_w, y)
        c.setFillColor(TEXT)
        c.setFont(FONT_BOLD, 7.2)
        c.drawString(x + 4, y - 12, label)
        c.setFont(FONT, 7.2)
        c.drawCentredString(x + label_w + value_w / 2, y - 12, value)


def _billing_pdf(document, document_type, company=None):
    """Create a branded A4 billing document using the supplied reference layout."""
    company = company or CompanyProfile.get_default()
    customer = document.customer
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    reference_number = getattr(document, "invoice_number" if document_type == "INVOICE" else "quotation_number", "")
    c.setTitle(f"{document_type.title()} {reference_number}")
    c.setAuthor(str(company.name or "ITGenius Computer"))

    # Reference frame: thin blue border with compact margins.
    border = 7 * mm
    left = 14 * mm
    right = PAGE_W - 14 * mm
    content_w = right - left
    c.setStrokeColor(BORDER)
    c.setLineWidth(1.15)
    c.rect(border, border, PAGE_W - 2 * border, PAGE_H - 2 * border, fill=0, stroke=1)

    # ------------------------------------------------------------------
    # Header
    # ------------------------------------------------------------------
    top = PAGE_H - 17 * mm
    logo_w, logo_h = 19 * mm, 24 * mm
    logo_path = _logo_path(company)
    if logo_path:
        try:
            c.drawImage(str(logo_path), left, top - logo_h + 25, width=logo_w, height=logo_h, preserveAspectRatio=True, mask="auto", anchor="c")
        except (OSError, ValueError):
            pass

    company_x = left + 29 * mm
    c.setFillColor(DARK_BLUE)
    c.setFont(FONT, 17)
    company_name = "ITGenius Computer" if document_type == "QUOTE" else str(company.name or "ITGenius Computer")
    c.drawString(company_x, top, company_name)
    c.setFillColor(TEXT)
    info_y = top - 15
    tagline = "Computer Repair & Software Development" if document_type == "QUOTE" else getattr(company, "tagline", "")
    if tagline:
        info_y = _draw_wrapped(c, tagline, company_x, info_y, 245, size=8.2, leading=10, max_lines=1)

    # The company-details block uses every available CompanyProfile contact field.
    info_y = top - logo_h - 8
    if company.address:
        info_y = _draw_contact_line(c, "location", _format_address(company.address), left + 2, info_y, 250, size=7.7, max_lines=2)
    for kind, label, value in (("web", "Website", company.website), ("phone", "Phone", company.phone), ("email", "Email", company.email), ("contact", "GSTIN", company.gst_number), ("contact", "PAN", company.pan_number)):
        if value:
            info_y = _draw_contact_line(c, kind, f"{label}: {value}", left + 2, info_y, 250, size=7.4)

    c.setFillColor(DARK_BLUE)
    c.setFont(FONT_BOLD, 25)
    c.drawRightString(right, top, document_type)
    _metadata(c, document, document_type, right - 92 * mm, top - 27, 92 * mm)

    # ------------------------------------------------------------------
    # Customer block - deliberately left aligned like the reference.
    # ------------------------------------------------------------------
    customer_top = top - 145
    customer_w = 235
    customer_h = 82
    _section(c, "CUSTOMER", left, customer_top, customer_w)
    c.setStrokeColor(colors.HexColor("#777777"))
    c.setLineWidth(0.6)
    c.rect(left, customer_top - customer_h, customer_w, customer_h, fill=0, stroke=1)
    details = [
        ("contact", str(getattr(customer, "name", "") or "")),
        ("building", str(getattr(customer, "company_name", "") or "")),
        ("location", _format_address(getattr(customer, "address", ""))),
        ("phone", str(getattr(customer, "phone", "") or "")),
        ("email", str(getattr(customer, "email", "") or "")),
    ]
    c.setFillColor(TEXT)
    if getattr(customer, "gst_number", ""):
        details.append(("contact", f"GSTIN: {customer.gst_number}"))
    cy = customer_top - 31
    for icon, detail in details:
        if detail.strip():
            cy = _draw_contact_line(c, icon, detail, left + 5, cy, customer_w - 10, size=7.8, max_lines=2)
            if cy < customer_top - customer_h + 8:
                break

    # ------------------------------------------------------------------
    # Item table. Fixed coordinates prevent Platypus from moving sections.
    # ------------------------------------------------------------------
    table_top = customer_top - customer_h - 17
    header_h = 18
    row_h = 20
    taxed_w = 48
    amount_w = 88
    desc_w = content_w - taxed_w - amount_w
    x0 = left
    x1 = x0 + desc_w
    x2 = x1 + taxed_w
    x3 = right

    c.setFillColor(BLUE)
    c.rect(x0, table_top - header_h, content_w, header_h, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont(FONT_BOLD, 8.5)
    c.drawString(x0 + 5, table_top - 12, "DESCRIPTION")
    c.drawCentredString((x1 + x2) / 2, table_top - 12, "TAXED")
    c.drawString(x2 + 5, table_top - 12, "AMOUNT")

    items = list(document.items.select_related("product").all())
    visible_rows = max(1, min(10, len(items)))
    if len(items) <= 3:
        visible_rows = 10
    table_bottom = table_top - header_h - visible_rows * row_h

    for i in range(visible_rows):
        row_top = table_top - header_h - i * row_h
        if i % 2 == 1:
            c.setFillColor(ROW_GREY)
            c.rect(x0, row_top - row_h, content_w, row_h, fill=1, stroke=0)
        c.setStrokeColor(GRID)
        c.setLineWidth(0.55)
        c.rect(x0, row_top - row_h, content_w, row_h, fill=0, stroke=1)
        c.line(x1, row_top - row_h, x1, row_top)
        c.line(x2, row_top - row_h, x2, row_top)

        if i < len(items):
            item = items[i]
            description = str(getattr(item, "description", "") or getattr(item.product, "name", ""))
            qty = _decimal(getattr(item, "quantity", 1))
            unit_price = _decimal(getattr(item, "unit_price", 0))
            if qty != 1:
                description += f" | Qty: {qty:g} × {_money(unit_price)}"
            c.setFillColor(TEXT)
            c.setFont(FONT, 7.8)
            c.drawString(x0 + 5, row_top - 8, description[:105])
            if _decimal(getattr(item, "gst_rate", 0)) > 0:
                c.setFont(FONT_BOLD, 8)
                c.drawCentredString((x1 + x2) / 2, row_top - 13, "X")
            c.setFont(FONT, 8)
            c.drawRightString(x3 - 5, row_top - 12, f"{_decimal(getattr(item, 'amount', 0)):,.2f}")

    # ------------------------------------------------------------------
    # Terms + totals, side by side like the supplied reference.
    # ------------------------------------------------------------------
    bottom_top = table_bottom - 12
    terms_w = 355
    totals_x = left + terms_w + 12
    totals_w = right - totals_x
    terms_h = 141

    _section(c, "TERMS AND CONDITIONS", left, bottom_top, terms_w)
    c.setStrokeColor(DARK_BLUE)
    c.setLineWidth(0.8)
    c.rect(left, bottom_top - terms_h, terms_w, terms_h, fill=0, stroke=1)

    company_terms = "invoice_terms" if document_type == "INVOICE" else "quotation_terms"
    terms = str(getattr(document, "terms", "") or getattr(company, company_terms, "") or "")
    lines = [line.strip() for line in terms.splitlines() if line.strip()]
    if not lines:
        lines = (
            [
                "Customer will be billed after indicating acceptance of this quote.",
                "Payment will be due prior to delivery of service and goods.",
                "Please fax or mail the signed price quote to the address above.",
            ]
            if document_type == "QUOTE"
            else [
                "Payment is due by the due date shown on this invoice.",
                "Please retain this invoice as proof of purchase.",
                "Please contact us if any information in this invoice requires correction.",
            ]
        )
    terms_bottom = bottom_top - terms_h
    ty = bottom_top - 30
    c.setFillColor(TEXT)
    for number, line in enumerate(lines, 1):
        ty = _draw_wrapped(c, f"{number}. {line}", left + 5, ty, terms_w - 10, size=7.5, leading=9, max_lines=2)
        if ty < terms_bottom + 64:
            break
    c.setStrokeColor(colors.HexColor("#C8D8F0"))
    c.setLineWidth(0.5)
    c.line(left + 5, terms_bottom + 58, left + terms_w - 5, terms_bottom + 58)
    c.setFillColor(DARK_BLUE if document_type == "QUOTE" else TEXT)
    c.setFont(FONT_ITALIC if document_type == "QUOTE" else FONT_BOLD, 7.7)
    acceptance_label = "Customer Acceptance (sign below):" if document_type == "QUOTE" else "Authorised signature (if required):"
    c.drawString(left + 5, terms_bottom + 45, acceptance_label)
    c.setFont(FONT, 7.7)
    c.drawString(left + 5, terms_bottom + 25, "X __________________________________")
    c.drawString(left + 5, terms_bottom + 12, "Print Name: _________________________")

    subtotal = _decimal(getattr(document, "subtotal", 0))
    discount = _decimal(getattr(document, "discount_amount", 0))
    tax = _decimal(getattr(document, "tax_amount", 0))
    taxable = max(subtotal - discount, Decimal("0.00"))
    tax_rate = (tax / taxable * Decimal("100")) if taxable else Decimal("0.00")
    total_rows = [
        ("Subtotal", f"{subtotal:,.2f}"),
        ("Taxable", f"{taxable:,.2f}"),
        ("Tax Rate", f"{tax_rate:.2f}%"),
        ("Tax Due", f"{tax:,.2f}"),
        ("Other", "-"),
    ]
    total_row_height = 22
    total_gap = 10
    total_y = bottom_top - 16
    totals_bottom = total_y - len(total_rows) * total_row_height - total_gap - 5
    c.setStrokeColor(DARK_BLUE)
    c.setLineWidth(0.8)
    c.rect(totals_x, totals_bottom, totals_w, bottom_top - totals_bottom, fill=0, stroke=1)
    c.setFont(FONT, 8)
    for label, value in total_rows:
        c.setFillColor(TEXT)
        c.drawString(totals_x + 7, total_y, label)
        c.drawRightString(right - 7, total_y, value)
        total_y -= total_row_height

    total_y -= total_gap

    c.setFillColor(YELLOW)
    c.setStrokeColor(DARK_BLUE)
    c.setLineWidth(0.8)
    c.rect(totals_x, total_y - 5, totals_w, 25, fill=1, stroke=1)
    c.setFillColor(TEXT)
    c.setFont(FONT_BOLD, 9.5)
    c.drawString(totals_x + 7, total_y + 4, "TOTAL")
    c.drawRightString(right - 7, total_y + 4, _money(getattr(document, "grand_total", 0)))

    # Footer.
    footer = " | ".join(str(v) for v in (company.phone, company.email) if v)
    c.setFillColor(TEXT)
    c.setFont(FONT, 7.5)
    c.drawCentredString(PAGE_W / 2, 72, f"If you have any questions about this {document_type.lower()}, please contact us.")
    if footer:
        c.drawCentredString(PAGE_W / 2, 58, footer)
    c.setFont(FONT_ITALIC, 9)
    c.drawCentredString(PAGE_W / 2, 43, "Thank You For Your Business!")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer


def quotation_pdf(quotation):
    return _billing_pdf(quotation, "QUOTE")


def invoice_pdf(invoice, company=None):
    return _billing_pdf(invoice, "INVOICE", company=company)
