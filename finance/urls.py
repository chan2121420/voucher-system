from rest_framework.routers import DefaultRouter
from . api import SaleViewSet, SaleReturnViewSet
from django.urls import path
from . views import *

app_name = 'finance'

router = DefaultRouter()
router.register(r'api/v1/sales', SaleViewSet, basename='sale')
router.register(r'api/v1/sale-returns', SaleReturnViewSet, basename='sale-return')

urlpatterns = [
    path('end_of_day/', end_of_day, name='end_of_day'),
    path('eod/detail/<int:id>/', eod_detail, name='eod_detail'),
    path('download/pdf/<int:id>/', download_eod_pdf, name='download_eod')
] + router.urls
