from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from .models import Sale, SaleReturn, Client, MonthlyPayment
from .serializers import (
    SaleSerializer, 
    SaleReturnSerializer, 
    ClientSerializer,
    MonthlyPaymentSerializer
)
from rest_framework.response import Response
from loguru import logger
from vouchers.models import Vouchers
from django.db import transaction
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class ClientViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing clients (casual and permanent members)
    """
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['get'])
    def payment_history(self, request, pk=None):
        """Get payment history for a specific client"""
        client = self.get_object()
        payments = MonthlyPayment.objects.filter(client=client)
        serializer = MonthlyPaymentSerializer(payments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def pending_payments(self, request, pk=None):
        """Get pending/overdue payments for a specific client"""
        client = self.get_object()
        payments = MonthlyPayment.objects.filter(
            client=client, 
            status__in=['pending', 'overdue']
        )
        serializer = MonthlyPaymentSerializer(payments, many=True)
        return Response(serializer.data)


class SaleViewSet(viewsets.ModelViewSet):
    """
    API endpoint for processing a sale
    """
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """
        Custom create method to handle multiple vouchers in a single sale and optionally create a client.
        Expected payload:
        {
            "voucher": [1, 2],
            "amount": 100.00,
            "sale-type": "hourly",
            "cashier": 1,
            "client": {
                "name": "John Doe",
                "phonenumber": "0771234567",
                "email": "john@example.com"
            }
        }
        """
        client_data = request.data.pop("client", None)
        client = None

        # Process client info only if provided
        if isinstance(client_data, dict) and client_data:
            raw_phone = client_data.get("phonenumber", "")
            raw_name = client_data.get("name", "")

            client_phone = str(raw_phone).strip() if raw_phone is not None else ""
            client_name = str(raw_name).strip() if raw_name is not None else ""

            # Only create/get a client if phone number exists
            if client_phone:
                client, created = Client.objects.get_or_create(
                    phonenumber=client_phone,
                    defaults={
                        "name": client_name,
                        "email": client_data.get("email", ""),
                    }
                )

                # If client exists but info differs, update it
                if not created:
                    updated = False
                    if client_name and client.name != client_name:
                        client.name = client_name
                        updated = True
                    if client_data.get("email") and client.email != client_data["email"]:
                        client.email = client_data["email"]
                        updated = True
                    if updated:
                        client.save()

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        vouchers = request.data.get("voucher", [])
        if not isinstance(vouchers, list):
            vouchers = [vouchers]

        vouchers = list(map(int, vouchers))
        existing_vouchers = set(Vouchers.objects.filter(id__in=vouchers, status='unused').values_list("id", flat=True))
        missing_vouchers = set(vouchers) - existing_vouchers

        if missing_vouchers:
            return Response(
                {"message": f"Vouchers {list(missing_vouchers)} do not exist or have been sold."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                # Mark vouchers as sold
                Vouchers.objects.filter(pk__in=vouchers).update(status="sold", active=True)

                # Save sale with or without client
                sale = serializer.save(client=client)

            logger.info(f"Sale {sale.id} created by {request.user} with client {client.id if client else 'None'}")

            sales_data = SaleSerializer(sale).data
            vouchers_data = list(Vouchers.objects.filter(id__in=vouchers).values(
                'id', 'voucher_no' ,'voucher_user'
            ))

            data = {
                'sales_data': sales_data,
                'vouchers_data': vouchers_data
            }

            return Response(data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error creating sale: {str(e)}")
            return Response(
                {"message": f"Error creating sale: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class MonthlyPaymentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing monthly membership payments
    """
    queryset = MonthlyPayment.objects.all()
    serializer_class = MonthlyPaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter payments by query parameters"""
        queryset = MonthlyPayment.objects.all()
        
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        client_id = self.request.query_params.get('client', None)
        if client_id:
            queryset = queryset.filter(client_id=client_id)
        
        month = self.request.query_params.get('month', None)
        if month:
            queryset = queryset.filter(payment_month=month)
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        """
        Create a monthly payment record and optionally process payment immediately.
        Expected payload:
        {
            "client": 1,
            "amount": 50.00,
            "payment_month": "2025-10-01",
            "due_date": "2025-10-05",
            "status": "pending",
            "notes": "October 2025 membership"
        }
        Or to process payment immediately:
        {
            "client": 1,
            "amount": 50.00,
            "payment_month": "2025-10-01",
            "process_payment": true,
            "payment_method": "mobile_money",
            "payment_reference": "MM123456",
            "cashier": 1
        }
        """
        process_payment = request.data.pop('process_payment', False)
        payment_method = request.data.pop('payment_method', 'cash')
        payment_reference = request.data.pop('payment_reference', '')
        cashier_id = request.data.pop('cashier', request.user.id)
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                monthly_payment = serializer.save()
                
                if process_payment:
                    client = monthly_payment.client
                    
                    sale = Sale.objects.create(
                        amount=monthly_payment.amount,
                        sale_type='monthly',
                        cashier_id=cashier_id,
                        client=client,
                        payment_method=payment_method,
                        payment_reference=payment_reference,
                        payment_month=monthly_payment.payment_month,
                        is_monthly_payment=True,
                        notes=monthly_payment.notes
                    )
                    
                    # Update monthly payment record
                    monthly_payment.sale = sale
                    monthly_payment.status = 'paid'
                    monthly_payment.payment_date = datetime.now()
                    monthly_payment.save()
                    
                    logger.info(f"Monthly payment {monthly_payment.id} processed with Sale {sale.id}")
                
                return Response(
                    MonthlyPaymentSerializer(monthly_payment).data,
                    status=status.HTTP_201_CREATED
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def process_payment(self, request, pk=None):
        """
        Process payment for an existing monthly payment record.
        Expected payload:
        {
            "payment_method": "mobile_money",
            "payment_reference": "MM123456",
            "cashier": 1
        }
        """
        monthly_payment = self.get_object()
        
        if monthly_payment.status == 'paid':
            return Response(
                {"message": "Payment has already been processed."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payment_method = request.data.get('payment_method', 'cash')
        payment_reference = request.data.get('payment_reference', '')
        cashier_id = request.data.get('cashier', request.user.id)
        
        with transaction.atomic():
            sale = Sale.objects.create(
                amount=monthly_payment.amount,
                sale_type='monthly',
                cashier_id=cashier_id,
                client=monthly_payment.client,
                payment_method=payment_method,
                payment_reference=payment_reference,
                payment_month=monthly_payment.payment_month,
                is_monthly_payment=True,
                notes=monthly_payment.notes
            )
            
            monthly_payment.sale = sale
            monthly_payment.status = 'paid'
            monthly_payment.payment_date = datetime.now()
            monthly_payment.save()
            
            logger.info(f"Monthly payment {monthly_payment.id} processed with Sale {sale.id}")
        
        return Response(
            MonthlyPaymentSerializer(monthly_payment).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['post'])
    def generate_monthly_payments(self, request):
        """
        Generate monthly payment records for all active permanent members.
        Expected payload:
        {
            "month": "2025-11-01"  # Optional, defaults to next month
        }
        """
        month_str = request.data.get('month')
        if month_str:
            payment_month = datetime.strptime(month_str, '%Y-%m-%d').date().replace(day=1)
        else:
            today = datetime.now().date()
            payment_month = (today.replace(day=1) + relativedelta(months=1))
        
        permanent_members = Client.objects.filter(
            client_type='permanent',
            is_active=True
        )
        
        created_count = 0
        skipped_count = 0
        
        with transaction.atomic():
            for client in permanent_members:
                existing = MonthlyPayment.objects.filter(
                    client=client,
                    payment_month=payment_month
                ).exists()
                
                if existing:
                    skipped_count += 1
                    continue
                
                due_date = payment_month.replace(day=5)
                
                MonthlyPayment.objects.create(
                    client=client,
                    amount=client.monthly_fee or 0,
                    payment_month=payment_month,
                    due_date=due_date,
                    status='pending'
                )
                created_count += 1
        
        logger.info(f"Generated {created_count} monthly payments for {payment_month.strftime('%B %Y')}")
        
        return Response({
            "message": f"Generated {created_count} payment records, skipped {skipped_count} existing records",
            "month": payment_month.strftime('%B %Y'),
            "created": created_count,
            "skipped": skipped_count
        })
    
    @action(detail=False, methods=['post'])
    def mark_overdue(self, request):
        """
        Mark pending payments as overdue if they're past due date.
        This should be run daily via a cron job or task scheduler.
        """
        today = datetime.now().date()
        
        updated = MonthlyPayment.objects.filter(
            status='pending',
            due_date__lt=today
        ).update(status='overdue')
        
        logger.info(f"Marked {updated} payments as overdue")
        
        return Response({
            "message": f"Marked {updated} payments as overdue"
        })


class SaleReturnViewSet(viewsets.ModelViewSet):
    """
    API endpoint for sale returns.
    """
    queryset = SaleReturn.objects.all()
    serializer_class = SaleReturnSerializer
    permission_classes = [IsAuthenticated]
