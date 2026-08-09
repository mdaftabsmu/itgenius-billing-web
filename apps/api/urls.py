from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet, InvoiceViewSet, ProductViewSet

router = DefaultRouter()
router.register("customers", CustomerViewSet, basename="api-customer")
router.register("products", ProductViewSet, basename="api-product")
router.register("invoices", InvoiceViewSet, basename="api-invoice")
urlpatterns = router.urls
