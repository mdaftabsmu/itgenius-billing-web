from decimal import Decimal, InvalidOperation
from io import BytesIO
from pathlib import Path

from django.utils.html import escape
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .models import CompanyProfile

BLUE = colors.HexColor("#2F69B5")
DARK_BLUE = colors.HexColor("#285FA8")
ROW_GREY = colors.HexColor("#F1F1F1")
YELLOW = colors.HexColor("#FFD43B")
BORDER = colors.HexColor("#2F69B5")
TEXT = colors.HexColor("#202020")
PAGE_MARGIN = 12 * mm
CONTENT_WIDTH = A4[0] - (PAGE_MARGIN * 2)  # 186 mm

FONT_NAME = "Helvetica"
FONT_BOLD = "Helvetica-Bold"
FONT_ITALIC = "Helvetica-Oblique"


def _register_inr_font():
    """Register a Unicode font when available so the ₹ symbol renders correctly."""
    global FONT_NAME, FONT_BOLD, FONT_ITALIC
    candidates = [
        Path(__file__).resolve().parent / "fonts" / "DejaVuSans.ttf",
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    ]
    regular = next((p for p in candidates if p.name == "DejaVuSans.ttf" and p.exists()), None)
    bold = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
    italic = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf")

    if regular and bold.exists() and italic.exists():
        try:
            pdfmetrics.registerFont(TTFont("DejaVuBilling", str(regular)))
            pdfmetrics.registerFont(TTFont("DejaVuBilling-Bold", str(bold)))
            pdfmetrics.registerFont(TTFont("DejaVuBilling-Italic", str(italic)))
            FONT_NAME = "DejaVuBilling"
            FONT_BOLD = "DejaVuBilling-Bold"
            FONT_ITALIC = "DejaVuBilling-Italic"
        except Exception:
            pass


_register_inr_font()


def _decimal(value):
    try:
        return Decimal(str(value or 0))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal("0.00")


def _money(value, symbol=True):
    amount = f"{_decimal(value):,.2f}"
    return f"₹ {amount}" if symbol else amount


def _clean(value):
    return escape(str(value or "")).replace("\n", "<br/>")


def _draw_page(canvas, doc):
    canvas.saveState()
    width, height = A4
    canvas.setStrokeColor(BORDER)
    canvas.setLineWidth(1.15)
    canvas.rect(7 * mm, 7 * mm, width - 14 * mm, height - 14 * mm)
    canvas.restoreState()


def _styles():
    base = getSampleStyleSheet()
    return {
        "section": ParagraphStyle(
            "quote_section", parent=base["Normal"], fontName=FONT_BOLD,
            fontSize=9, leading=10.5, textColor=colors.white,
        ),
        "body": ParagraphStyle(
            "quote_body", parent=base["Normal"], fontName=FONT_NAME,
            fontSize=8.2, leading=10, textColor=TEXT,
        ),
        "small": ParagraphStyle(
            "quote_small", parent=base["Normal"], fontName=FONT_NAME,
            fontSize=7.3, leading=8.8, textColor=TEXT,
        ),
        "company": ParagraphStyle(
            "quote_company", parent=base["Normal"], fontName=FONT_NAME,
            fontSize=17, leading=19, textColor=colors.HexColor("#E8942E"),
        ),
        "tagline": ParagraphStyle(
            "quote_tagline", parent=base["Normal"], fontName=FONT_NAME,
            fontSize=8, leading=9.5, textColor=TEXT,
        ),
        "quote": ParagraphStyle(
            "quote_title", parent=base["Normal"], fontName=FONT_BOLD,
            fontSize=24, leading=25, alignment=TA_RIGHT, textColor=DARK_BLUE,
        ),
        "footer": ParagraphStyle(
            "quote_footer", parent=base["Normal"], fontName=FONT_ITALIC,
            fontSize=9, leading=11, alignment=TA_CENTER, textColor=TEXT,
        ),
        "center": ParagraphStyle(
            "quote_center", parent=base["Normal"], fontName=FONT_NAME,
            fontSize=8.2, leading=10, alignment=TA_CENTER, textColor=TEXT,
        ),
        "right": ParagraphStyle(
            "quote_right", parent=base["Normal"], fontName=FONT_NAME,
            fontSize=8.2, leading=10, alignment=TA_RIGHT, textColor=TEXT,
        ),
        "right_small": ParagraphStyle(
            "quote_right_small", parent=base["Normal"], fontName=FONT_NAME,
            fontSize=7.5, leading=9, alignment=TA_RIGHT, textColor=TEXT,
        ),
    }


def _metadata_table(quotation, styles):
    rows = [
        ["DATE", _clean(quotation.quotation_date)],
        ["QUOTE #", _clean(quotation.quotation_number)],
        ["CUSTOMER ID", _clean(getattr(quotation.customer, "customer_code", "-"))],
        ["VALID UNTIL", _clean(quotation.valid_until or "-")],
    ]
    table = Table(
        [[Paragraph(label, styles["small"]), Paragraph(value, styles["center"])] for label, value in rows],
        colWidths=[31 * mm, 34 * mm],
        rowHeights=[6.5 * mm] * 4,
    )
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.45, colors.HexColor("#999999")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F6F6F6")),
        ("FONTNAME", (0, 0), (0, -1), FONT_BOLD),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (1, 0), (1, -1), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
    ]))
    return table


def _company_header(company, quotation, styles):
    logo = Spacer(1, 1)
    if company.logo:
        try:
            logo = Image(company.logo.path, width=18 * mm, height=16 * mm, kind="proportional")
        except (OSError, ValueError):
            logo = Spacer(1, 1)

    company_text = [
        Paragraph(_clean(company.name), styles["company"]),
    ]
    if company.tagline:
        company_text.append(Paragraph(_clean(company.tagline), styles["tagline"]))
    if company.address:
        company_text.append(Paragraph(_clean(company.address), styles["small"]))
    contact = "<br/>".join(
        f"{label}: {_clean(value)}"
        for label, value in (
            ("Website", company.website),
            ("Phone", company.phone),
            ("Email", company.email),
            ("GSTIN", company.gst_number),
        ) if value
    )
    if contact:
        company_text.append(Paragraph(contact, styles["small"]))

    left = Table([[logo, company_text]], colWidths=[22 * mm, 98 * mm])
    left.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))

    right = Table([
        [Paragraph("QUOTE", styles["quote"])],
        [_metadata_table(quotation, styles)],
    ], colWidths=[65 * mm], rowHeights=[15 * mm, 28 * mm])
    right.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))

    header = Table([[left, right]], colWidths=[120 * mm, 65 * mm])
    header.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return header


def _customer_table(quotation, styles):
    customer = quotation.customer
    values = [
        _clean(customer.name),
        _clean(getattr(customer, "company_name", "")),
        _clean(getattr(customer, "address", "")),
        _clean(getattr(customer, "phone", "")),
        _clean(getattr(customer, "email", "")),
    ]
    if getattr(customer, "gst_number", ""):
        values.append(f"GSTIN: {_clean(customer.gst_number)}")
    details = "<br/>".join(v for v in values if v)
    table = Table([
        [Paragraph("CUSTOMER", styles["section"])],
        [Paragraph(details or "-", styles["body"])],
    ], colWidths=[78 * mm], rowHeights=[7 * mm, 30 * mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), BLUE),
        ("BOX", (0, 0), (-1, -1), 0.65, colors.HexColor("#777777")),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return table


def _items_table(quotation, styles):
    rows = [[
        Paragraph("DESCRIPTION", styles["section"]),
        Paragraph("TAXED", styles["section"]),
        Paragraph("AMOUNT", styles["section"]),
    ]]
    items = list(quotation.items.select_related("product").all())

    for item in items:
        description = _clean(item.description or item.product.name)
        qty = _decimal(item.quantity)
        if qty != 1:
            description += f"<br/><font size='7'>Qty: {qty:g} × {_money(item.unit_price)}</font>"
        rows.append([
            Paragraph(description, styles["body"]),
            Paragraph("X" if _decimal(item.gst_rate) > 0 else "", styles["center"]),
            Paragraph(f"{_decimal(item.amount):,.2f}", styles["right"]),
        ])

    # The reference has a large blank writing area. Ten item rows gives a compact
    # A4 layout while leaving enough room for terms and totals.
    minimum_rows = 10
    while len(rows) < minimum_rows + 1:
        rows.append([Paragraph("&nbsp;", styles["body"]), Paragraph("", styles["body"]), Paragraph("", styles["body"])])

    heights = [7 * mm] + [7 * mm] * (len(rows) - 1)
    table = Table(rows, colWidths=[126 * mm, 20 * mm, 40 * mm], rowHeights=heights, repeatRows=1)
    commands = [
        ("BACKGROUND", (0, 0), (-1, 0), BLUE),
        ("GRID", (0, 0), (-1, -1), 0.6, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 1.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5),
    ]
    for index in range(1, len(rows)):
        if index % 2 == 0:
            commands.append(("BACKGROUND", (0, index), (-1, index), ROW_GREY))
    table.setStyle(TableStyle(commands))
    return table


def _terms_table(quotation, company, styles):
    terms = quotation.terms or company.quotation_terms
    lines = [line.strip() for line in (terms or "").splitlines() if line.strip()]
    if not lines:
        lines = [
            "Customer will be billed after indicating acceptance of this quote.",
            "Payment will be due prior to delivery of service and goods.",
            "Please contact us if you need any clarification about this quotation.",
        ]
    terms_text = "<br/>".join(f"{i}. {_clean(line)}" for i, line in enumerate(lines, 1))
    terms_text += (
        "<br/><br/><i><b>Customer Acceptance (sign below):</b></i>"
        "<br/><br/>X _________________________________"
        "<br/>Print Name: _________________________"
    )
    table = Table([
        [Paragraph("TERMS AND CONDITIONS", styles["section"])],
        [Paragraph(terms_text, styles["body"])],
    ], colWidths=[110 * mm], rowHeights=[7 * mm, 47 * mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), BLUE),
        ("BOX", (0, 0), (-1, -1), 0.65, colors.HexColor("#777777")),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return table


def _totals_table(quotation, styles):
    subtotal = _decimal(quotation.subtotal)
    discount = _decimal(quotation.discount_amount)
    taxable = max(subtotal - discount, Decimal("0.00"))
    tax = _decimal(quotation.tax_amount)
    rate = (tax / taxable * Decimal("100")) if taxable else Decimal("0.00")

    rows = [
        ("Subtotal", f"{subtotal:,.2f}"),
        ("Taxable", f"{taxable:,.2f}"),
        ("Discount", f"{discount:,.2f}"),
        ("Tax Rate", f"{rate:.2f}%"),
        ("Tax Due", f"{tax:,.2f}"),
        ("Other", "-"),
        ("TOTAL", _money(quotation.grand_total)),
    ]
    data = [[Paragraph(label, styles["body"]), Paragraph(value, styles["right"])] for label, value in rows]
    data[-1] = [
        Paragraph("TOTAL", ParagraphStyle("total_label", parent=styles["body"], fontName=FONT_BOLD, fontSize=10)),
        Paragraph(_money(quotation.grand_total), ParagraphStyle("total_value", parent=styles["right"], fontName=FONT_BOLD, fontSize=10)),
    ]
    table = Table(data, colWidths=[40 * mm, 36 * mm], rowHeights=[6.8 * mm] * 7)
    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ("BACKGROUND", (0, -1), (-1, -1), YELLOW),
        ("LINEABOVE", (0, -1), (-1, -1), 0.8, colors.HexColor("#B28B00")),
    ]))
    return table


def quotation_pdf(quotation):
    """Generate an A4 quotation closely matching the supplied reference image."""
    company = CompanyProfile.get_default()
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=PAGE_MARGIN,
        leftMargin=PAGE_MARGIN,
        topMargin=10 * mm,
        bottomMargin=10 * mm,
        title=f"Quotation {quotation.quotation_number}",
        author=company.name,
        subject="Quotation",
    )
    styles = _styles()
    story = [
        _company_header(company, quotation, styles),
        Spacer(1, 4 * mm),
        _customer_table(quotation, styles),
        Spacer(1, 4 * mm),
        _items_table(quotation, styles),
        Spacer(1, 4 * mm),
    ]

    bottom = Table(
        [[_terms_table(quotation, company, styles), _totals_table(quotation, styles)]],
        colWidths=[110 * mm, 76 * mm],
    )
    bottom.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(bottom)
    story.append(Spacer(1, 4 * mm))

    contact = " | ".join(x for x in [company.phone, company.email] if x)
    if contact:
        story.append(Paragraph(_clean(contact), ParagraphStyle(
            "quote_contact", parent=styles["body"], alignment=TA_CENTER, fontSize=7.5,
        )))
    story.append(Spacer(1, 1 * mm))
    story.append(Paragraph("Thank You For Your Business!", styles["footer"]))

    doc.build(story, onFirstPage=_draw_page, onLaterPages=_draw_page)
    buffer.seek(0)
    return buffer
