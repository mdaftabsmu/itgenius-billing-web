from decimal import Decimal
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from .models import CompanyProfile


def _money(value):
    return f"₹ {Decimal(value):,.2f}"


def quotation_pdf(quotation):
    company = CompanyProfile.get_default()
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=15*mm, leftMargin=15*mm, topMargin=12*mm, bottomMargin=12*mm)
    styles = getSampleStyleSheet()
    right = ParagraphStyle("right", parent=styles["Normal"], alignment=TA_RIGHT)
    title = ParagraphStyle("title", parent=styles["Title"], fontSize=18, leading=22)
    story = []
    if company.logo:
        try:
            story.append(Image(company.logo.path, width=35*mm, height=18*mm, kind="proportional"))
        except (OSError, ValueError):
            pass
    story += [Paragraph(company.name, title)]
    if company.tagline: story.append(Paragraph(company.tagline, styles["Normal"]))
    if company.address: story.append(Paragraph(company.address.replace("\n", "<br/>"), styles["Normal"]))
    contact = " | ".join(x for x in [company.phone, company.email, company.website, company.gst_number] if x)
    if contact: story.append(Paragraph(contact, styles["Normal"]))
    story += [Spacer(1, 8), Paragraph(f"QUOTATION #{quotation.quotation_number}", title)]
    story.append(Paragraph(f"Date: {quotation.quotation_date} &nbsp;&nbsp; Valid Until: {quotation.valid_until or '-'}", styles["Normal"]))
    story.append(Spacer(1, 6))
    customer = quotation.customer
    customer_text = f"<b>Bill To</b><br/>{customer.name}<br/>{customer.company_name}<br/>{customer.address}<br/>{customer.phone} {customer.email}<br/>GST: {customer.gst_number}"
    story.append(Paragraph(customer_text, styles["Normal"]))
    story.append(Spacer(1, 10))
    data = [["#", "Product", "Qty", "Unit Price", "GST", "Tax", "Amount"]]
    for index, item in enumerate(quotation.items.all(), 1):
        data.append([index, Paragraph(item.product.name, styles["Normal"]), str(item.quantity), _money(item.unit_price), f"{item.gst_rate}%", _money(item.tax_amount), _money(item.amount)])
    table = Table(data, colWidths=[9*mm, 62*mm, 18*mm, 27*mm, 17*mm, 23*mm, 27*mm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#eeeeee")), ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("ALIGN", (2,1), (-1,-1), "RIGHT"), ("VALIGN", (0,0), (-1,-1), "TOP"), ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0,0), (-1,0), 7), ("TOPPADDING", (0,0), (-1,0), 7),
    ]))
    story += [table, Spacer(1, 8)]
    totals = [["Subtotal", _money(quotation.subtotal)], ["Discount", _money(quotation.discount_amount)], ["Tax", _money(quotation.tax_amount)], ["Grand Total", _money(quotation.grand_total)]]
    total_table = Table(totals, colWidths=[45*mm, 45*mm], hAlign="RIGHT")
    total_table.setStyle(TableStyle([("ALIGN", (1,0), (1,-1), "RIGHT"), ("FONTNAME", (0,-1), (-1,-1), "Helvetica-Bold"), ("LINEABOVE", (0,-1), (-1,-1), 1, colors.black)]))
    story.append(total_table)
    if quotation.notes: story += [Spacer(1, 10), Paragraph("<b>Notes</b><br/>" + quotation.notes.replace("\n", "<br/>"), styles["Normal"])]
    terms = quotation.terms or company.quotation_terms
    if terms: story += [Spacer(1, 8), Paragraph("<b>Terms & Conditions</b><br/>" + terms.replace("\n", "<br/>"), styles["Normal"])]
    doc.build(story)
    buffer.seek(0)
    return buffer
