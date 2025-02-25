from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Sale, SaleReturn
from .serializers import SaleSerializer, SaleReturnSerializer


class SaleViewSet(viewsets.ModelViewSet):
    """
    API endpoint for processing a sale
    """
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """
        Custom create method to handle multiple vouchers in a single sale.
        Expected payload:
        {
            "voucher": [1, 2],
            "amount": 100.00,  
            "type": "hourly",
            "cashier": 1  # Cashier ID
        }
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            sale = serializer.save()  # `create` in serializer handles M2M
            return Response(SaleSerializer(sale).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class SaleReturnViewSet(viewsets.ModelViewSet):
    """
    API endpoint for sale returns.
    """
    queryset = SaleReturn.objects.all()
    serializer_class = SaleReturnSerializer
    permission_classes = [IsAuthenticated]
