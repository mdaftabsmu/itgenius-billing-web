import logging
from decimal import Decimal
from django.db import transaction
from .models import Product

logger = logging.getLogger("billing")

@transaction.atomic
def adjust_stock(product: Product, quantity: Decimal, reason: str = "manual"):
    quantity = Decimal(str(quantity))
    new_quantity = product.stock_quantity + quantity
    if new_quantity < 0:
        raise ValueError("Stock quantity cannot become negative")
    product.stock_quantity = new_quantity
    product.save(update_fields=["stock_quantity", "updated_at"])
    logger.info("Stock adjusted | product=%s | delta=%s | reason=%s | balance=%s", product.product_code, quantity, reason, new_quantity)
    return product
