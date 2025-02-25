from . import views
from . import api
from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = 'vouchers'

router = DefaultRouter()
router.register(r'files', api.VoucherFileViewSet)
router.register(r'logs', api.VoucherLogViewSet)
router.register(r'categories', api.VoucherCategoryViewSet)
router.register(r'users', api.VoucherUserViewSet)

urlpatterns = [
    path('voucherLogs/', views.voucherLog, name='voucherLogs'),
    path('addCategory/', views.addCategory, name='addCategory'),
    path("voucherList/", views.vouchersList,  name="voucherList"),
    path("voucherFiles/", views.voucherFiles,  name="voucherFiles"),
    path('printVoucher/<int:pk>/', views.printVoucher, name='printVoucher'),
    path('addVoucherUser/<int:pk>/', views.addVoucherUser, name='addVoucherUser'),
    path("populateVouchers/<int:pk>", views.populateVouchers,  name="populateVouchers"),

    #api urls
    path('api/v1/', include(router.urls)),
]
