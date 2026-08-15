from decimal import Decimal, InvalidOperation
from io import BytesIO
from pathlib import Path

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


def _metadata(c, quotation, x, top, width=92 * mm):
    row_h = 18
    label_w = 42 * mm
    value_w = width - label_w
    rows = [
        ("DATE", _date(getattr(quotation, "quotation_date", None))),
        ("QUOTE #", str(getattr(quotation, "quotation_number", "-"))),
        ("CUSTOMER ID", str(getattr(quotation.customer, "customer_code", "-"))),
        ("VALID UNTIL", _date(getattr(quotation, "valid_until", None))),
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


def quotation_pdf(quotation):
    """Create an A4 quotation using fixed coordinates to match the supplied reference."""
    company = CompanyProfile.get_default()
    customer = quotation.customer
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.setTitle(f"Quotation {quotation.quotation_number}")
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
    logo_w, logo_h = 22 * mm, 18 * mm
    if getattr(company, "logo", None):
        try:
            c.drawImage(company.logo.path, left, top - logo_h + 2, width=logo_w, height=logo_h, preserveAspectRatio=True, mask="auto", anchor="c")
        except (OSError, ValueError):
            pass

    company_x = left + 26 * mm
    c.setFillColor(ORANGE)
    c.setFont(FONT, 17)
    c.drawString(company_x, top, str(company.name or "ITGenius Computer"))
    c.setFillColor(TEXT)
    info_y = top - 16
    info_y = _draw_wrapped(c, company.address, company_x, info_y, 250, size=7.7, leading=9, max_lines=2)
    for label, value in (("Website", company.website), ("Phone", company.phone), ("Email", company.email), ("GSTIN", company.gst_number)):
        if value:
            info_y = _draw_wrapped(c, f"{label}: {value}", company_x, info_y, 250, size=7.4, leading=9, max_lines=1)

    c.setFillColor(DARK_BLUE)
    c.setFont(FONT_BOLD, 25)
    c.drawRightString(right, top, "QUOTE")
    _metadata(c, quotation, right - 92 * mm, top - 27, 92 * mm)

    # ------------------------------------------------------------------
    # Customer block - deliberately left aligned like the reference.
    # ------------------------------------------------------------------
    customer_top = top - 104
    customer_w = 235
    customer_h = 82
    _section(c, "CUSTOMER", left, customer_top, customer_w)
    c.setStrokeColor(colors.HexColor("#777777"))
    c.setLineWidth(0.6)
    c.rect(left, customer_top - customer_h, customer_w, customer_h, fill=0, stroke=1)
    details = [
        str(getattr(customer, "name", "") or ""),
        str(getattr(customer, "company_name", "") or ""),
        str(getattr(customer, "address", "") or ""),
        str(getattr(customer, "phone", "") or ""),
        str(getattr(customer, "email", "") or ""),
    ]
    if getattr(customer, "gst_number", ""):
        details.append(f"GSTIN: {customer.gst_number}")
    cy = customer_top - 31
    for detail in details:
        if detail.strip():
            cy = _draw_wrapped(c, detail, left + 5, cy, customer_w - 10, size=7.8, leading=9.5, max_lines=2)
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

    items = list(quotation.items.select_related("product").all())
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
    terms_w = 365
    totals_x = left + terms_w + 10
    totals_w = right - totals_x
    terms_h = 132

    _section(c, "TERMS AND CONDITIONS", left, bottom_top, terms_w)
    c.setStrokeColor(colors.HexColor("#777777"))
    c.rect(left, bottom_top - terms_h, terms_w, terms_h, fill=0, stroke=1)

    terms = str(getattr(quotation, "terms", "") or getattr(company, "quotation_terms", "") or "")
    lines = [line.strip() for line in terms.splitlines() if line.strip()]
    if not lines:
        lines = [
            "Customer will be billed after indicating acceptance of this quote.",
            "Payment will be due prior to delivery of service and goods.",
            "Please contact us if any information in this quotation requires correction.",
        ]
    ty = bottom_top - 31
    for number, line in enumerate(lines, 1):
        ty = _draw_wrapped(c, f"{number}. {line}", left + 5, ty, terms_w - 10, size=7.5, leading=9, max_lines=2)
        if ty < bottom_top - 77:
            break
    c.setFillColor(TEXT)
    c.setFont(FONT_BOLD, 7.7)
    c.drawString(left + 5, bottom_top - 88, "Customer Acceptance (sign below):")
    c.setFont(FONT, 7.7)
    c.drawString(left + 5, bottom_top - 108, "X __________________________________")
    c.drawString(left + 5, bottom_top - 120, "Print Name: _________________________")

    subtotal = _decimal(getattr(quotation, "subtotal", 0))
    discount = _decimal(getattr(quotation, "discount_amount", 0))
    tax = _decimal(getattr(quotation, "tax_amount", 0))
    taxable = max(subtotal - discount, Decimal("0.00"))
    tax_rate = (tax / taxable * Decimal("100")) if taxable else Decimal("0.00")
    total_rows = [
        ("Subtotal", f"{subtotal:,.2f}"),
        ("Taxable", f"{taxable:,.2f}"),
        ("Tax Rate", f"{tax_rate:.2f}%"),
        ("Tax Due", f"{tax:,.2f}"),
        ("Other", "-"),
    ]
    total_y = bottom_top - 13
    c.setFont(FONT, 8)
    for label, value in total_rows:
        c.setFillColor(TEXT)
        c.drawString(totals_x, total_y, label)
        c.drawRightString(right, total_y, value)
        total_y -= 19

    c.setFillColor(YELLOW)
    c.rect(totals_x, total_y - 4, totals_w, 22, fill=1, stroke=0)
    c.setFillColor(TEXT)
    c.setFont(FONT_BOLD, 9.5)
    c.drawString(totals_x + 4, total_y + 3, "TOTAL")
    c.drawRightString(right - 4, total_y + 3, _money(getattr(quotation, "grand_total", 0)))

    # Footer.
    footer = " | ".join(str(v) for v in (company.phone, company.email) if v)
    c.setFillColor(TEXT)
    c.setFont(FONT, 7.5)
    if footer:
        c.drawCentredString(PAGE_W / 2, 58, footer)
    c.setFont(FONT_ITALIC, 9)
    c.drawCentredString(PAGE_W / 2, 43, "Thank You For Your Business!")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer
