from rest_framework import status, viewsets, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import *
from .serializers import *
from .permissions import IsAdminOrReadOnly


class VoucherFileViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Voucher File operations.
    Allows CRUD operations on voucher files.
    """
    queryset = VoucherFile.objects.all()
    serializer_class = VoucherFileSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'created_at']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name']


class VoucherListAPIView(APIView):
    """
    API endpoint for listing unused vouchers.
    Allows filtering by file category.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        vouchers = Vouchers.objects.filter(status='unused')
        category = request.query_params.get('category')
        
        if category:
            vouchers = vouchers.filter(file__category=category)
            
        serializer = VouchersSerializer(vouchers, many=True)
        return Response(serializer.data)


class VoucherLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for voucher logs.
    Read-only operations to maintain audit integrity.
    """
    queryset = VoucherLogs.objects.all()
    serializer_class = VoucherLogsSerializer
    permission_classes = [IsAuthenticated]
    # filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    # filterset_fields = ['voucher', 'user', 'action_type', 'created_at']
    ordering_fields = ['created_at']


class VoucherCategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for voucher categories.
    Allows CRUD operations on categories.
    """
    queryset = VoucherCategory.objects.all()
    serializer_class = VoucherCategorySerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def create(self, request, *args, **kwargs):
        # Check if category with the same name already exists
        name = request.data.get('name')
        if name and VoucherCategory.objects.filter(name__iexact=name).exists():
            return Response(
                {"error": "Category with this name already exists"},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().create(request, *args, **kwargs)


class VoucherUserViewSet(viewsets.ModelViewSet):
    """
        API endpoint for voucher users.
        Allows CRUD operations on voucher users.
    """
    queryset = VoucherUser.objects.all()
    serializer_class = VoucherUserSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['role', 'department']
    search_fields = ['user__username', 'user__email', 'department']



