from django.contrib import admin
from .models import *

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'phonenumber', 'client_type', 'is_active', 'monthly_fee', 'date']
    list_filter = ['client_type', 'is_active']
    search_fields = ['name', 'phonenumber', 'email']

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['id', 'sale_type', 'amount', 'payment_method', 'is_monthly_payment', 'client', 'date']
    list_filter = ['sale_type', 'payment_method', 'is_monthly_payment']
    search_fields = ['client__name', 'payment_reference']

@admin.register(MonthlyPayment)
class MonthlyPaymentAdmin(admin.ModelAdmin):
    list_display = ['client', 'amount', 'payment_month', 'due_date', 'status', 'payment_date']
    list_filter = ['status', 'payment_month']
    search_fields = ['client__name', 'client__phonenumber']

admin.site.register(EndOfDay)
admin.site.register(EndOfDayItem)
admin.site.register(SaleReturn)