from django.contrib import admin
from vouchers.models import *

admin.site.register(Vouchers)
admin.site.register(VoucherFile)
admin.site.register(VoucherLogs)
admin.site.register(VoucherUser)
admin.site.register(VoucherCategory)

