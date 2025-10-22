from rest_framework import serializers
from .models import Sale, SaleReturn, Client, MonthlyPayment
from datetime import datetime


class ClientSerializer(serializers.ModelSerializer):
    """
    Serializer for the Client model.
    
    Handles the serialization and deserialization of Client objects.
    
    Fields:
        id (int): The unique identifier for the client (read-only).
        name (str): The name of the client.
        phonenumber (str): The client's phone number, used as a unique identifier.
        email (str): The client's email address.
        date (datetime): The date the client was added to the system (read-only).
        client_type (str): Type of client - casual or permanent member.
        membership_start_date (date): Start date of membership for permanent members.
        membership_end_date (date): End date of membership for permanent members.
        monthly_fee (decimal): Monthly fee for permanent members.
        is_active (bool): Whether the client is active.
    """
    class Meta:
        model = Client
        fields = ["id", "name", "phonenumber", "email", "date", "client_type", 
                  "membership_start_date", "membership_end_date", "monthly_fee", "is_active"]
        read_only_fields = ["id", "date"]


class SaleSerializer(serializers.ModelSerializer):
    """
    Serializer for the Sale model.
    
    Handles the serialization and deserialization of Sale objects.
    Provides validation for vouchers and maintains relationships with clients.
    
    Fields:
        id (int): The unique identifier for the sale (read-only).
        voucher (list): A list of voucher IDs associated with this sale.
        amount (decimal): The total monetary value of the sale.
        sale_type (str): The type of the sale (hourly, day desk, meeting room, monthly).
        date (datetime): The date and time when the sale was created (read-only).
        cashier (int): The ID of the user who processed the sale.
        client (int): The ID of the client associated with this sale (optional).
        payment_method (str): Payment method used.
        payment_reference (str): Reference number for the payment.
        notes (str): Additional notes about the sale.
        payment_month (date): Month this payment covers (for monthly payments).
        is_monthly_payment (bool): Whether this is a monthly membership payment.
    
    Note:
        The voucher field accepts multiple voucher IDs for handling bulk sales.
        Client is optional and can be set to null if it's an anonymous sale.
    """
    voucher = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Sale.voucher.field.related_model.objects.all(),
        required=False
    )

    client = serializers.PrimaryKeyRelatedField(
        queryset=Client.objects.all(), 
        required=False
    )
    
    class Meta:
        model = Sale
        fields = ['id', 'voucher', 'amount', 'sale_type', 'date', 'cashier', 'client',
                  'payment_method', 'payment_reference', 'notes', 'payment_month', 'is_monthly_payment']
        read_only_fields = ['id', 'date']
    
    def validate(self, data):
        # If it's a monthly payment, client is required
        if data.get('is_monthly_payment') and not data.get('client'):
            raise serializers.ValidationError("Client is required for monthly payments")
        
        # If sale_type is monthly, set is_monthly_payment to True
        if data.get('sale_type') == 'monthly':
            data['is_monthly_payment'] = True
            
            # Set payment_month if not provided
            if not data.get('payment_month'):
                data['payment_month'] = datetime.now().date().replace(day=1)
        
        return data


class SaleReturnSerializer(serializers.ModelSerializer):
    """
    Serializer for the SaleReturn model.
    
    Handles the serialization and deserialization of SaleReturn objects.
    Used to process refunds or returns for existing sales.
    
    Fields:
        id (int): The unique identifier for the return (read-only).
        sale (int): The ID of the original sale being returned.
        amount (decimal): The monetary amount being returned.
        date (datetime): The date and time when the return was processed (read-only).
        cashier (int): The ID of the user who processed the return.
        reason (str): Reason for the return.
    
    Note:
        The sale field relates this return to an existing sale in the system.
        Amount can be less than or equal to the original sale amount.
    """
    sale = serializers.PrimaryKeyRelatedField(queryset=Sale.objects.all())
    
    class Meta:
        model = SaleReturn
        fields = ['id', 'sale', 'amount', 'date', 'cashier', 'reason']
        read_only_fields = ['id', 'date']


class MonthlyPaymentSerializer(serializers.ModelSerializer):
    """
    Serializer for the MonthlyPayment model.
    
    Handles monthly membership payments for permanent members.
    """
    client_name = serializers.CharField(source='client.name', read_only=True)
    client_phone = serializers.CharField(source='client.phonenumber', read_only=True)
    
    class Meta:
        model = MonthlyPayment
        fields = ['id', 'client', 'client_name', 'client_phone', 'sale', 'amount', 
                  'payment_month', 'due_date', 'payment_date', 'status', 'notes', 
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']