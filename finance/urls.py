from rest_framework.routers import DefaultRouter
from . api import SaleViewSet, SaleReturnViewSet

app_name = 'finance'

router = DefaultRouter()
router.register(r'api/v1/sales', SaleViewSet, basename='sale')
router.register(r'api/v1/sale-returns', SaleReturnViewSet, basename='sale-return')

urlpatterns = router.urls