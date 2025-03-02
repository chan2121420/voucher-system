from django.db import models
from django.utils.translation import gettext_lazy as _

class VoucherCategory(models.Model):
    name = models.CharField(max_length=50)
    
    class Meta:
        verbose_name = _("VoucherCategory")
        verbose_name_plural = _("VoucherCategories")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("VoucherCategory_detail", kwargs={"pk": self.pk})

class VoucherFile(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    file = models.FileField(upload_to='vouchers', max_length=100)
    category = models.ForeignKey("vouchers.VoucherCategory", on_delete=models.CASCADE)
    date_created = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=50, default='not populated')

    class Meta:
        ordering = ['-date_created']
        verbose_name = _("VoucherFile")
        verbose_name_plural = _("VoucherFiles")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("VoucherFile_detail", kwargs={"pk": self.pk})

class Vouchers(models.Model):
    voucher_password = models.CharField(max_length=50)
    voucher_username = models.CharField(max_length=50)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    file = models.ForeignKey("vouchers.VoucherFile", on_delete=models.CASCADE)
    date_created = models.DateField(auto_now_add=True)
    date_used = models.DateField(auto_now=True)
    status = models.CharField(max_length=50, default='unused')
    
    class Meta:
        ordering = ['-date_created']
        verbose_name = _("Vouchers")
        verbose_name_plural = _("Vouchers")

    def __str__(self):
        return self.voucher_no

    def get_absolute_url(self):
        return reverse("Vouchers_detail", kwargs={"pk": self.pk})
    
class VoucherLogs(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    action = models.CharField(max_length=50)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_created']
        verbose_name = _("VoucherLogs")
        verbose_name_plural = _("VoucherLogs")

    def __str__(self):
        return f'{self.user} : {self.action}'

    def get_absolute_url(self):
        return reverse("VoucherLogs_detail", kwargs={"pk": self.pk})

class VoucherUser(models.Model):
    voucher_no = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    phonenumber = models.CharField(max_length=50) 
    email = models.EmailField(max_length=50)   
    date_created = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = _("VoucherUser")
        verbose_name_plural = _("VoucherUsers")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("VoucherUser_detail", kwargs={"pk": self.pk})



