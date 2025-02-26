from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from .models import Sale, SaleReturn, Client
from .serializers import SaleSerializer, SaleReturnSerializer
from rest_framework.response import Response
from loguru import logger
from vouchers.models import Vouchers
from django.db import transaction



class SaleViewSet(viewsets.ModelViewSet):
    """
    API endpoint for processing a sale
    """
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    # permission_classes = [IsAuthenticated]

    from django.db import transaction

def create(self, request, *args, **kwargs):
    """
    Custom create method to handle multiple vouchers in a single sale and create a client.
    Expected payload:
    {
        "voucher": [1, 2],
        "amount": 100.00,  
        "type": "hourly",
        "cashier": 1,  # Cashier ID
        "client": {
            "name": "casy",
            "phonenumber": "1234567890",
            "email": "casy@example.com"
        }
    }
    """
    serializer = self.get_serializer(data=request.data)

    if serializer.is_valid():
        vouchers = request.data.get("voucher", [])

        if type(vouchers) != list:
            vouchers = [vouchers]

        vouchers = list(map(int, vouchers)) 

        existing_vouchers = set(Vouchers.objects.filter(id__in=vouchers, status='unused').values_list("id", flat=True))
        missing_vouchers = set(vouchers) - existing_vouchers

        if missing_vouchers:
            return Response(
                {"message": f"Vouchers {list(missing_vouchers)} do not exist or have been sold."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            # Create Client
            client_data = request.data.get("client", {})
            client, created = Client.objects.get_or_create(
                phonenumber=client_data.get("phonenumber"),
                defaults={
                    "name": client_data.get("name", ""),
                    "email": client_data.get("email", ""),
                }
            )

            # Bulk update vouchers as sold
            Vouchers.objects.filter(pk__in=vouchers).update(status="sold")

            # Save sale and associate client
            sale = serializer.save(client=client)
        
        logger.info(f"Sale {sale.id} created by {request.user} with Client {client.id}")

        return Response(SaleSerializer(sale).data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class SaleReturnViewSet(viewsets.ModelViewSet):
    """
    API endpoint for sale returns.
    """
    queryset = SaleReturn.objects.all()
    serializer_class = SaleReturnSerializer
    permission_classes = [IsAuthenticated]
