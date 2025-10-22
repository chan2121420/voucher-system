from django.db import models

class Client(models.Model):
    CLIENT_TYPE_CHOICES = [
        ('casual', 'Casual'),
        ('permanent', 'Permanent Member'),
    ]
    
    name = models.CharField(max_length=50)
    phonenumber = models.CharField(max_length=50) 
    email = models.EmailField(max_length=50)   
    date = models.DateField(auto_now_add=True)
    
    # NEW FIELDS FOR PERMANENT MEMBERS
    client_type = models.CharField(max_length=20, choices=CLIENT_TYPE_CHOICES, default='casual')
    membership_start_date = models.DateField(null=True, blank=True)
    membership_end_date = models.DateField(null=True, blank=True)
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Sale(models.Model):
    voucher = models.ManyToManyField("vouchers.Vouchers", blank=True)  # Made blank=True
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    sale_type = models.CharField(max_length=50, choices=[
        ('hourly', 'hourly'), 
        ('day desk', 'day desk'),
        ('meeting room', 'meeting room'),
        ('monthly', 'monthly'),
    ])
    date = models.DateTimeField(auto_now_add=True)
    cashier = models.ForeignKey("users.User", on_delete=models.CASCADE)
    client = models.ForeignKey("finance.Client", on_delete=models.CASCADE, null=True, blank=True)
    
    # NEW FIELDS FOR MONTHLY PAYMENTS
    payment_method = models.CharField(max_length=50, choices=[
        ('cash', 'Cash'),
        ('mobile_money', 'Mobile Money'),
        ('bank_transfer', 'Bank Transfer'),
        ('card', 'Card'),
    ], default='cash')
    payment_reference = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    payment_month = models.DateField(null=True, blank=True, help_text="Month this payment covers")
    is_monthly_payment = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f'{self.sale_type} - {self.amount}'


class SaleReturn(models.Model):
    sale = models.ForeignKey("finance.Sale", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    cashier = models.ForeignKey("users.User", on_delete=models.CASCADE)
    reason = models.TextField(blank=True, null=True)  # NEW FIELD

    def __str__(self):
        return f'{self.sale} - {self.amount}'


class EndOfDay(models.Model):
    date = models.DateField()
    pdf = models.FileField(upload_to='end_of_days/', null=True, blank=True)
    amount = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    
    # NEW FIELDS FOR PAYMENT METHOD BREAKDOWN
    total_sales_count = models.IntegerField(default=0)
    cash_amount = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    mobile_money_amount = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    bank_transfer_amount = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    card_amount = models.DecimalField(default=0, max_digits=10, decimal_places=2)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"EOD - {self.date}"


class EndOfDayItem(models.Model):
    eod = models.ForeignKey(EndOfDay, on_delete=models.CASCADE, null=True, related_name='items')
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)

    def __str__(self):
        return f"EOD Item - {self.eod.date}"


# NEW MODEL FOR MONTHLY PAYMENT TRACKING
class MonthlyPayment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='monthly_payments')
    sale = models.OneToOneField(Sale, on_delete=models.SET_NULL, null=True, blank=True, related_name='monthly_payment_record')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_month = models.DateField(help_text="Month this payment is for")
    due_date = models.DateField()
    payment_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-payment_month']
        unique_together = ['client', 'payment_month']

    def __str__(self):
        return f"{self.client.name} - {self.payment_month.strftime('%B %Y')} - {self.status}"