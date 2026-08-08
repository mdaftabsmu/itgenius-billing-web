import logging
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from .models import Quotation
from apps.core.pdf import quotation_pdf

logger = logging.getLogger("billing")

@login_required
def quotation_pdf_view(request, pk):
    quotation = get_object_or_404(Quotation.objects.prefetch_related("items__product"), pk=pk)
    logger.info("Quotation PDF generated | quotation=%s | user=%s", quotation.quotation_number, request.user.username)
    return FileResponse(quotation_pdf(quotation), as_attachment=True, filename=f"{quotation.quotation_number}.pdf", content_type="application/pdf")
