from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


def build_invoice_pdf(invoice, company=None):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=15 * mm, leftMargin=15 * mm, topMargin=15 * mm, bottomMargin=15 * mm)
    styles = getSampleStyleSheet()
    story = []
    company_name = getattr(company, "name", "ITGenius Computer") if company else "ITGenius Computer"
    story.append(Paragraph(f"<b>{company_name}</b>", styles["Title"]))
    if company:
        contact = " | ".join(filter(None, [getattr(company, "phone", ""), getattr(company, "email", ""), getattr(company, "gst_number", "")]))
        if contact:
            story.append(Paragraph(contact, styles["Normal"]))
    story.append(Spacer(1, 8))
    story.append(Paragraph(f"<b>INVOICE: {invoice.invoice_number}</b>", styles["Heading2"]))
    story.append(Paragraph(f"Date: {invoice.invoice_date} | Due: {invoice.due_date or '-'}", styles["Normal"]))
    story.append(Paragraph(f"Customer: {invoice.customer.name}", styles["Normal"]))
    story.append(Spacer(1, 8))
    data = [["#", "Product", "Qty", "Rate", "GST", "Tax", "Amount"]]
    for index, item in enumerate(invoice.items.all(), 1):
        data.append([index, item.product.name, item.quantity, f"{item.unit_price:.2f}", f"{item.gst_rate}%", f"{item.tax_amount:.2f}", f"{item.amount:.2f}"])
    table = Table(data, repeatRows=1, colWidths=[8 * mm, 62 * mm, 18 * mm, 25 * mm, 18 * mm, 22 * mm, 25 * mm])
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey), ("GRID", (0, 0), (-1, -1), 0.4, colors.grey), ("ALIGN", (2, 1), (-1, -1), "RIGHT"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    story.append(table)
    story.append(Spacer(1, 10))
    totals = [["Subtotal", f"₹{invoice.subtotal:.2f}"], ["Discount", f"₹{invoice.discount_amount:.2f}"], ["Tax", f"₹{invoice.tax_amount:.2f}"], ["Grand Total", f"₹{invoice.grand_total:.2f}"], ["Paid", f"₹{invoice.paid_amount:.2f}"], ["Balance Due", f"₹{invoice.balance_due:.2f}"]]
    total_table = Table(totals, colWidths=[140 * mm, 35 * mm], hAlign="RIGHT")
    total_table.setStyle(TableStyle([("ALIGN", (1, 0), (1, -1), "RIGHT"), ("FONTNAME", (0, 3), (-1, 3), "Helvetica-Bold"), ("LINEABOVE", (0, 3), (-1, 3), 0.8, colors.black)]))
    story.append(total_table)
    if invoice.notes:
        story.append(Spacer(1, 8)); story.append(Paragraph(f"Notes: {invoice.notes}", styles["Normal"]))
    if invoice.terms:
        story.append(Spacer(1, 5)); story.append(Paragraph(f"Terms: {invoice.terms}", styles["Normal"]))
    doc.build(story)
    buffer.seek(0)
    return buffer
