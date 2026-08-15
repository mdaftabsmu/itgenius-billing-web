from decimal import Decimal, InvalidOperation
from io import BytesIO

from django.utils.html import escape
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .models import CompanyProfile

BLUE = colors.HexColor("#1F5FBF")
DARK_BLUE = colors.HexColor("#174A94")
LIGHT_BLUE = colors.HexColor("#EAF2FF")
ROW_GREY = colors.HexColor("#F3F3F3")
YELLOW = colors.HexColor("#FFC928")
BORDER = colors.HexColor("#1F5FBF")
TEXT = colors.HexColor("#202020")


def _decimal(value):
    try:
        return Decimal(value or 0)
    except (InvalidOperation, TypeError, ValueError):
        return Decimal("0.00")


def _money(value):
    return f"₹ { _decimal(value):,.2f}"


def _clean(value):
    return escape(str(value or "")).replace("\n", "<br/>")


def _draw_page(canvas, doc):
    canvas.saveState()
    width, height = A4
    canvas.setStrokeColor(BORDER)
    canvas.setLineWidth(1.1)
    canvas.rect(8 * mm, 8 * mm, width - 16 * mm, height - 16 * mm)
    canvas.restoreState()


def _header_styles(styles):
    return {
        "section": ParagraphStyle(
            "section", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=9.5,
            leading=11, textColor=colors.white,
        ),
        "body": ParagraphStyle(
            "body", parent=styles["Normal"], fontName="Helvetica", fontSize=8.5,
            leading=11, textColor=TEXT,
        ),
        "small": ParagraphStyle(
            "small", parent=styles["Normal"], fontName="Helvetica", fontSize=7.5,
            leading=9.5, textColor=TEXT,
        ),
        "company": ParagraphStyle(
            "company", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=17,
            leading=19, textColor=DARK_BLUE,
        ),
        "tagline": ParagraphStyle(
            "tagline", parent=styles["Normal"], fontName="Helvetica", fontSize=8.5,
            leading=10, textColor=TEXT,
        ),
        "quote": ParagraphStyle(
            "quote", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=25,
            leading=27, alignment=TA_RIGHT, textColor=DARK_BLUE,
        ),
        "footer": ParagraphStyle(
            "footer", parent=styles["Normal"], fontName="Helvetica-Oblique", fontSize=8.5,
            leading=11, alignment=TA_CENTER, textColor=DARK_BLUE,
        ),
    }


def quotation_pdf(quotation):
    """Generate a professional A4 quotation matching the requested reference layout."""
    company = CompanyProfile.get_default()
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=13 * mm,
        bottomMargin=13 * mm,
        title=f"Quotation {quotation.quotation_number}",
        author=company.name,
    )

    styles = _header_styles(getSampleStyleSheet())
    story = []

    # Header: company identity on the left and quotation metadata on the right.
    logo_flowable = Spacer(1, 1)
    if company.logo:
        try:
            logo_flowable = Image(company.logo.path, width=22 * mm, height=18 * mm, kind="proportional")
        except (OSError, ValueError):
            logo_flowable = Spacer(1, 1)

    company_lines = [
        Paragraph(_clean(company.name), styles["company"]),
        Paragraph(_clean(company.tagline), styles["tagline"]) if company.tagline else Spacer(1, 1),
        Paragraph(_clean(company.address), styles["body"]) if company.address else Spacer(1, 1),
    ]
    contact_lines = "<br/>".join(
        f"{label}: {_clean(value)}"
        for label, value in (
            ("Website", company.website),
            ("Phone", company.phone),
            ("Email", company.email),
            ("GSTIN", company.gst_number),
        )
        if value
    )
    if contact_lines:
        company_lines.append(Paragraph(contact_lines, styles["small"]))

    metadata = [
        [Paragraph("DATE", styles["small"]), Paragraph(_clean(quotation.quotation_date), styles["small"])],
        [Paragraph("QUOTE #", styles["small"]), Paragraph(_clean(quotation.quotation_number), styles["small"])],
        [Paragraph("CUSTOMER ID", styles["small"]), Paragraph(_clean(getattr(quotation.customer, "customer_code", "-")), styles["small"])],
        [Paragraph("VALID UNTIL", styles["small"]), Paragraph(_clean(quotation.valid_until or "-"), styles["small"])],
    ]
    metadata_table = Table(metadata, colWidths=[31 * mm, 32 * mm])
    metadata_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.45, colors.grey),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F7F7F7")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("ALIGN", (1, 0), (1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))

    header = Table([
        [Table([[logo_flowable, company_lines]], colWidths=[27 * mm, 92 * mm]),
         Table([[Paragraph("QUOTE", styles["quote"])], [metadata_table]], colWidths=[68 * mm])]
    ], colWidths=[119 * mm, 68 * mm])
    header.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
    story += [header, Spacer(1, 6 * mm)]

    # Customer block.
    customer = quotation.customer
    customer_details = [
        _clean(customer.name),
        _clean(getattr(customer, "company_name", "")),
        _clean(getattr(customer, "address", "")),
        _clean(getattr(customer, "phone", "")),
        _clean(getattr(customer, "email", "")),
        f"GSTIN: {_clean(getattr(customer, 'gst_number', ''))}" if getattr(customer, "gst_number", "") else "",
    ]
    customer_details = "<br/>".join(x for x in customer_details if x)
    customer_table = Table([[Paragraph("CUSTOMER", styles["section"])], [Paragraph(customer_details or "-", styles["body"])]], colWidths=[82 * mm])
    customer_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), BLUE),
        ("BOX", (0, 0), (-1, -1), 0.6, colors.grey),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, 0), 4),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 4),
        ("TOPPADDING", (0, 1), (-1, 1), 6),
        ("BOTTOMPADDING", (0, 1), (-1, 1), 7),
    ]))
    story += [customer_table, Spacer(1, 6 * mm)]

    # Itemized description table.
    item_header = [
        Paragraph("DESCRIPTION", styles["section"]),
        Paragraph("TAXED", styles["section"]),
        Paragraph("AMOUNT (₹)", styles["section"]),
    ]
    rows = [item_header]
    items = list(quotation.items.all())
    for item in items:
        taxable_marker = "X" if _decimal(item.gst_rate) > 0 else ""
        description = _clean(item.description or item.product.name)
        if _decimal(item.quantity) != 1:
            description += f"<br/><font size='7'>Qty: {_decimal(item.quantity):g} × {_money(item.unit_price)}</font>"
        rows.append([
            Paragraph(description, styles["body"]),
            Paragraph(taxable_marker, ParagraphStyle("tax", parent=styles["body"], alignment=TA_CENTER)),
            Paragraph(f"{_decimal(item.amount):,.2f}", ParagraphStyle("amt", parent=styles["body"], alignment=TA_RIGHT)),
        ])

    # Keep the reference-style open writing area when there are only a few line items.
    minimum_rows = 12
    for _ in range(max(0, minimum_rows - len(items))):
        rows.append([Paragraph("&nbsp;", styles["body"]), Paragraph("", styles["body"]), Paragraph("", styles["body"])])

    item_table = Table(rows, colWidths=[128 * mm, 18 * mm, 36 * mm], repeatRows=1, rowHeights=None)
    item_style = [
        ("BACKGROUND", (0, 0), (-1, 0), BLUE),
        ("GRID", (0, 0), (-1, -1), 0.55, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, 0), 5),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 5),
    ]
    for row_index in range(1, len(rows)):
        if row_index % 2 == 0:
            item_style.append(("BACKGROUND", (0, row_index), (-1, row_index), ROW_GREY))
    item_table.setStyle(TableStyle(item_style))
    story += [item_table, Spacer(1, 5 * mm)]

    # Terms on the left and totals on the right.
    terms = quotation.terms or company.quotation_terms
    terms_lines = [line.strip() for line in (terms or "").splitlines() if line.strip()]
    if not terms_lines:
        terms_lines = [
            "Customer will be billed after indicating acceptance of this quote.",
            "Payment will be due prior to delivery of service and goods.",
            "Please contact us if any information in this quotation requires correction.",
        ]
    terms_text = "<br/>".join(f"{index}. {_clean(line)}" for index, line in enumerate(terms_lines, 1))
    terms_text += "<br/><br/><i><b>Customer Acceptance (sign below):</b></i><br/><br/>X _________________________________<br/>Print Name: _________________________"
    terms_table = Table([[Paragraph("TERMS AND CONDITIONS", styles["section"])], [Paragraph(terms_text, styles["body"])]], colWidths=[108 * mm])
    terms_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), BLUE),
        ("BOX", (0, 0), (-1, -1), 0.6, colors.grey),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, 0), 4),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 4),
        ("TOPPADDING", (0, 1), (-1, 1), 6),
        ("BOTTOMPADDING", (0, 1), (-1, 1), 7),
    ]))

    taxable = max(_decimal(quotation.subtotal) - _decimal(quotation.discount_amount), Decimal("0.00"))
    effective_rate = (_decimal(quotation.tax_amount) / taxable * Decimal("100")) if taxable else Decimal("0.00")
    totals_rows = [
        [Paragraph("Subtotal", styles["body"]), Paragraph(f"{_decimal(quotation.subtotal):,.2f}", ParagraphStyle("tr1", parent=styles["body"], alignment=TA_RIGHT))],
        [Paragraph("Taxable", styles["body"]), Paragraph(f"{taxable:,.2f}", ParagraphStyle("tr2", parent=styles["body"], alignment=TA_RIGHT))],
        [Paragraph("Discount", styles["body"]), Paragraph(f"{_decimal(quotation.discount_amount):,.2f}", ParagraphStyle("tr3", parent=styles["body"], alignment=TA_RIGHT))],
        [Paragraph("Tax Rate", styles["body"]), Paragraph(f"{effective_rate:.2f}%", ParagraphStyle("tr4", parent=styles["body"], alignment=TA_RIGHT))],
        [Paragraph("Tax Due", styles["body"]), Paragraph(f"{_decimal(quotation.tax_amount):,.2f}", ParagraphStyle("tr5", parent=styles["body"], alignment=TA_RIGHT))],
        [Paragraph("Other", styles["body"]), Paragraph("-", ParagraphStyle("tr6", parent=styles["body"], alignment=TA_RIGHT))],
        [Paragraph("TOTAL (₹)", ParagraphStyle("total_label", parent=styles["body"], fontName="Helvetica-Bold", fontSize=10)), Paragraph(f"{_decimal(quotation.grand_total):,.2f}", ParagraphStyle("total_value", parent=styles["body"], fontName="Helvetica-Bold", fontSize=10, alignment=TA_RIGHT))],
    ]
    totals_table = Table(totals_rows, colWidths=[38 * mm, 38 * mm], rowHeights=[7 * mm] * 7)
    totals_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ("BACKGROUND", (0, -1), (-1, -1), YELLOW),
        ("LINEABOVE", (0, -1), (-1, -1), 0.8, colors.HexColor("#C49A00")),
    ]))
    totals_table.hAlign = "RIGHT"

    bottom = Table([[terms_table, totals_table]], colWidths=[108 * mm, 78 * mm])
    bottom.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
    story.append(bottom)

    story += [Spacer(1, 5 * mm)]
    footer_contact = " | ".join(x for x in [company.phone, company.email, company.website] if x)
    if footer_contact:
        story.append(Paragraph(_clean(footer_contact), ParagraphStyle("contact", parent=styles["body"], alignment=TA_CENTER)))
    story.append(Paragraph("Thank You For Your Business!", styles["footer"]))

    doc.build(story, onFirstPage=_draw_page, onLaterPages=_draw_page)
    buffer.seek(0)
    return buffer
