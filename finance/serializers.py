from rest_framework import serializers
from .models import Sale, SaleReturn

class SaleSerializer(serializers.ModelSerializer):
    voucher = serializers.PrimaryKeyRelatedField(many=True, queryset=Sale.voucher.field.related_model.objects.all())

    class Meta:
        model = Sale
        fields = ['id', 'voucher', 'amount', 'type', 'date', 'cashier']


class SaleReturnSerializer(serializers.ModelSerializer):
    sale = serializers.PrimaryKeyRelatedField(queryset=Sale.objects.all())

    class Meta:
        model = SaleReturn
        fields = ['id', 'sale', 'amount', 'date', 'cashier']
