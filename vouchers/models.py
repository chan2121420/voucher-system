from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

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
    STATUS_CHOICES = [
        ('unused', 'Unused'),
        ('used', 'Used'),
        ('expired', 'Expired'),
        ('printed', 'Printed'),
    ]
    
    voucher_no = models.CharField(max_length=100, unique=True)  # pfSense voucher code
    voucher_password = models.CharField(max_length=50, blank=True, null=True)  # Optional for pfSense
    voucher_username = models.CharField(max_length=50, blank=True, null=True)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)  # Staff user who created it
    file = models.ForeignKey("vouchers.VoucherFile", on_delete=models.CASCADE)
    date_created = models.DateField(auto_now_add=True)
    date_used = models.DateTimeField(null=True, blank=True)  # When voucher was actually used
    date_printed = models.DateTimeField(null=True, blank=True)  # When voucher was printed
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='unused')
    active = models.BooleanField(default=False)
    
    # pfSense specific fields
    validity_duration = models.IntegerField(default=24, help_text="Validity in hours")  # How long voucher is valid after activation
    expiry_time = models.DateTimeField(null=True, blank=True)  # Absolute expiry time
    bandwidth_up = models.IntegerField(null=True, blank=True, help_text="Upload bandwidth in Kbps")
    bandwidth_down = models.IntegerField(null=True, blank=True, help_text="Download bandwidth in Kbps")
    pfsense_roll_id = models.IntegerField(null=True, blank=True)  # pfSense voucher roll ID
    synced_to_pfsense = models.BooleanField(default=False)  # Track if synced to pfSense
    
    class Meta:
        ordering = ['-date_created']
        verbose_name = _("Voucher")
        verbose_name_plural = _("Vouchers")

    def __str__(self):
        return f"{self.voucher_no} - {self.status}"

    def get_absolute_url(self):
        return reverse("Vouchers_detail", kwargs={"pk": self.pk})


class VoucherLogs(models.Model):
    ACTION_CHOICES = [
        ('create', 'Created'),
        ('populate', 'Populated'),
        ('print', 'Printed'),
        ('use', 'Used'),
        ('sync', 'Synced to pfSense'),
        ('expire', 'Expired'),
    ]
    
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    action = models.CharField(max_length=200)
    action_type = models.CharField(max_length=20, choices=ACTION_CHOICES, default='create')
    voucher = models.ForeignKey("vouchers.Vouchers", on_delete=models.SET_NULL, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)  # Track IP for API requests

    class Meta:
        ordering = ['-date_created']
        verbose_name = _("VoucherLog")
        verbose_name_plural = _("VoucherLogs")

    def __str__(self):
        return f'{self.user} : {self.action}'

    def get_absolute_url(self):
        return reverse("VoucherLogs_detail", kwargs={"pk": self.pk})


class VoucherUser(models.Model):
    voucher = models.OneToOneField("vouchers.Vouchers", on_delete=models.CASCADE, related_name='voucher_user')
    voucher_no = models.CharField(max_length=100)  # Denormalized for quick lookup
    name = models.CharField(max_length=100)
    phonenumber = models.CharField(max_length=50) 
    email = models.EmailField(max_length=100, blank=True, null=True)   
    date_created = models.DateField(auto_now_add=True)
    
    # Additional fields for tracking
    device_mac = models.CharField(max_length=17, blank=True, null=True)  # MAC address from pfSense
    last_used_ip = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        verbose_name = _("VoucherUser")
        verbose_name_plural = _("VoucherUsers")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("VoucherUser_detail", kwargs={"pk": self.pk})


class PfSenseConfig(models.Model):
    """Store pfSense connection configuration"""
    name = models.CharField(max_length=100, default="Default pfSense")
    host = models.CharField(max_length=255, help_text="pfSense host/IP")
    port = models.IntegerField(default=443)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=255)  # Consider encrypting this
    use_ssl = models.BooleanField(default=True)
    verify_ssl = models.BooleanField(default=False)
    captive_portal_zone = models.CharField(max_length=100, default="zone1", help_text="Captive portal zone name")
    is_active = models.BooleanField(default=True)
    last_sync = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = _("PfSense Configuration")
        verbose_name_plural = _("PfSense Configurations")

    def __str__(self):
        return f"{self.name} ({self.host})"