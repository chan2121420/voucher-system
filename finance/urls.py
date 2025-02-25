from rest_framework.routers import DefaultRouter
from . api import SaleViewSet, SaleReturnViewSet

router = DefaultRouter()
router.register(r'sales', SaleViewSet, basename='sale')
router.register(r'sale-returns', SaleReturnViewSet, basename='sale-return')

urlpatterns = router.urls