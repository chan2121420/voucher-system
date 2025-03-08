from django.core.management.base import BaseCommand
from django.utils import timezone
from vouchers.models import Vouchers

class Command(BaseCommand):
    help = 'Deactivate expired vouchers'

    def handle(self, *args, **options):
        expired_vouchers = Vouchers.objects.filter(
            active=True,
            expiry_time__lte=timezone.now()
        )
        count = expired_vouchers.count()
        expired_vouchers.update(active=False)
        self.stdout.write(
            self.style.SUCCESS(f'Successfully deactivated {count} expired vouchers')
        )