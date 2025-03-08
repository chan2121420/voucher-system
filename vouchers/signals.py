from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from .models import Sale, Vouchers
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
import datetime

@receiver(m2m_changed, sender=Sale.voucher.through)
def handle_voucher_activation(sender, instance, action, **kwargs):
    """
    When vouchers are added to a sale, set their expiry time based on sale_type
    """
    if action == 'post_add':
        voucher_ids = kwargs.get('pk_set', [])
        if not voucher_ids:
            return
            
        if instance.sale_type == 'hourly':
            expiry_time = instance.date + timedelta(hours=1)

        elif instance.sale_type == 'day desk':
            today = instance.date.date()

            expiry_time = timezone.make_aware(
                datetime.combine(today, datetime.max.time())
            )
        elif instance.sale_type == 'meeting room':
            expiry_time = instance.date + timedelta(hours=2)

        elif instance.sale_type == 'monthly':
            expiry_time = instance.date + timedelta(days=30)
        else:
            expiry_time = instance.date + timedelta(hours=1)
            
        # Update the vouchers with the calculated expiry time
        with transaction.atomic():
            Vouchers.objects.filter(id__in=voucher_ids).update(
                active=True,
                expiry_time=expiry_time
            )
        
        # Schedule the deactivation task
        for voucher_id in voucher_ids:
            schedule_voucher_deactivation(voucher_id)