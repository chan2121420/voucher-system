from django_q.tasks import schedule
from django_q.models import Schedule
import datetime
from . models import Vouchers
from loguru import logger

def schedule_voucher_deactivation(voucher_id):
    """Schedule a task to deactivate a voucher when it expires"""
    voucher = Vouchers.objects.get(id=voucher_id)
    
    Schedule.objects.filter(name=f'deactivate_voucher_{voucher_id}').delete()
    
    schedule(
        'your_app.tasks.deactivate_voucher',
        voucher_id,
        name=f'deactivate_voucher_{voucher_id}',
        schedule_type='O',  # One-time task
        next_run=voucher.expiry_time
    )

def deactivate_voucher(voucher_id):
    """Deactivate a voucher by setting active=False"""
    try:
        voucher = Vouchers.objects.get(id=voucher_id)
        if voucher.active and voucher.expiry_time and datetime.today.now() >= voucher.expiry_time:
            voucher.active = False
            voucher.save()
            logger(f"Voucher {voucher.code} deactivated")
    except Vouchers.DoesNotExist:
        logger(f"Voucher with ID {voucher_id} not found")