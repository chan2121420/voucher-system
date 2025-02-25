from datetime import date
from vouchers.models import *
from django.shortcuts import render
from django.contrib.auth.decorators import login_required 

@login_required(login_url='/users/login/')
def dashboard(request): 
    vouchers = VoucherUser.objects.filter(date_created = date.today())
    return render(request, 'dashboard.html', {
        'vouchers':vouchers,
        'count':vouchers.count(),
    })
