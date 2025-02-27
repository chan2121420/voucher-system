from rest_framework import serializers
from .models import Sale, SaleReturn, Client

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ["id", "name", "phonenumber", "email", "date"]
        read_only_fields = ["id", "date"]

class SaleSerializer(serializers.ModelSerializer):
    voucher = serializers.PrimaryKeyRelatedField(many=True, queryset=Sale.voucher.field.related_model.objects.all())
    client = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all(), required=False)  # silence the id(s) for dict creation

    class Meta:
        model = Sale
        fields = ['id', 'voucher', 'amount', 'sale_type', 'date', 'cashier', 'client']
        read_only_fields = ['id', 'date']

        
        
class SaleReturnSerializer(serializers.ModelSerializer):
    sale = serializers.PrimaryKeyRelatedField(queryset=Sale.objects.all())

    class Meta:
        model = SaleReturn
        fields = ['id', 'sale', 'amount', 'date', 'cashier']
        read_only_fields = ['id', 'date']

