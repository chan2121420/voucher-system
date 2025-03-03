from rest_framework import serializers
from .models import Sale, SaleReturn, Client

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
    """
    class Meta:
        model = Client
        fields = ["id", "name", "phonenumber", "email", "date"]
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
    
    Note:
        The voucher field accepts multiple voucher IDs for handling bulk sales.
        Client is optional and can be set to null if it's an anonymous sale.
    """
    voucher = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Sale.voucher.field.related_model.objects.all()
    )

    client = serializers.PrimaryKeyRelatedField(
        queryset=Client.objects.all(), 
        required=False
    ) # for dict creation to remove id from serializer validation
    
    class Meta:
        model = Sale
        fields = ['id', 'voucher', 'amount', 'sale_type', 'date', 'cashier', 'client']
        read_only_fields = ['id', 'date']
    

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
    
    Note:
        The sale field relates this return to an existing sale in the system.
        Amount can be less than or equal to the original sale amount.
    """
    sale = serializers.PrimaryKeyRelatedField(queryset=Sale.objects.all())
    
    class Meta:
        model = SaleReturn
        fields = ['id', 'sale', 'amount', 'date', 'cashier']
        read_only_fields = ['id', 'date']