from django.db import models

class Sale(models.Model):
    voucher = models.ManyToManyField("vouchers.Vouchers")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=50, choices=[
        ('hourly', 'hourly'), 
        ('day desk', 'day desk'),
        ('meeting room', 'meeting room'),
        ('monthly', 'monthly'),
    ])
    date = models.DateTimeField(auto_now_add=True)
    cashier = models.ForeignKey("users.User", on_delete=models.CASCADE)


    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f'{self.voucher} - {self.amount}'


class SaleReturn(models.Model):
    sale = models.ForeignKey("finance.Sale", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    cashier = models.ForeignKey("users.User", on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.sale} - {self.amount}'

