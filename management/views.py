from datetime import date
from vouchers.models import *
from django.shortcuts import render
from django.contrib.auth.decorators import login_required 
from finance.models import Sale
from django.db.models import Sum
from datetime import timedelta
from django.utils import timezone
from loguru import logger
import datetime

today = datetime.datetime.today()

@login_required(login_url='/users/login/')
def dashboard(request): 
    filter = request.GET.get('filter', '')
    start_day = request.GET.get('start', '')
    end_day = request.GET.get('filter', '')

    vouchers = VoucherUser.objects.filter(date_created = date.today())

    total_sales = sales(filter, start_day, end_day)

    return render(request, 'dashboard.html', {
        'vouchers':vouchers,
        'count':vouchers.count(),
        
        #totals
        'todays_sales':Sale.objects.filter(date__date=today).aggregate(Sum('amount'))['amount__sum'] or 0.00,
        'total_sales':total_sales
    })


def sales(filter, start_day=None, end_day=None):
    
    if filter == 'week':
        start_of_week = today - timedelta(days=today.weekday())  
        end_of_week = start_of_week + timedelta(days=6) 

        return total_sales if total_sales else 0
    
    elif filter == 'month':
        start_of_month = today.replace(day=1)  
        end_of_month = today.replace(day=28) + timedelta(days=4)  
        end_of_month = end_of_month - timedelta(days=end_of_month.day) 
        total_sales = Sale.objects.filter(date__range=[start_of_month, end_of_month]).aggregate(Sum('amount'))['amount__sum']
        return total_sales if total_sales else 0
    
    elif filter == 'year':
        start_of_year = today.replace(month=1, day=1) 
        end_of_year = today.replace(month=12, day=31)  
        total_sales = Sale.objects.filter(date__range=[start_of_year, end_of_year]).aggregate(Sum('amount'))['amount__sum']
        return total_sales if total_sales else 0
    
    elif filter == 'custom' and start_day and end_day:
        total_sales = Sale.objects.filter(date__range=[start_day, end_day]).aggregate(Sum('amount'))['amount__sum']
        return total_sales if total_sales else 0
    
    return Sale.objects.all().aggregate(Sum('amount'))['amount__sum']



    
