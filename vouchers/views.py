from vouchers.models import VoucherFile, Vouchers, VoucherCategory, VoucherLogs, VoucherUser
from django.db.models import Q
from django.contrib import messages
from .serializers import *
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required 
from vouchers.forms import AddVoucherFileForm, VoucherUserForm
from django.http import JsonResponse
from django.template.loader import render_to_string
from loguru import logger
from django.utils import timezone


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@login_required(login_url='/users/login/')
def voucherFiles(request):
    files = VoucherFile.objects.all()
    form = AddVoucherFileForm()
    if request.method == 'POST':
        form = AddVoucherFileForm(request.POST, request.FILES)
        if form.is_valid():
            voucher_object = form.save(commit=False)
            voucher_object.user = request.user
            voucher_object.save()
            
            voucher_log = VoucherLogs(
                user=request.user,
                action=f"{request.user.username} created file {request.POST['name']}",
                action_type='create',
                ip_address=get_client_ip(request)
            )
            voucher_log.save()
            messages.success(request, 'Voucher file created successfully')
            return redirect('vouchers:voucherFiles')

    return render(request, 'vouchers/vouchers.html', {
        'voucherFiles': files,
        'form': form
    })


@login_required(login_url='/users/login/')
def vouchersList(request):
    page = int(request.GET.get('page', 1))
    page_size = 20

    vou = Vouchers.objects.all()
    categories = VoucherCategory.objects.all()

    q = request.GET.get('q', '')
    status_filter = request.GET.get('status', 'unused')

    filtered_vouchers = vou.filter(status=status_filter)
    
    if q:
        try:
            filtered_vouchers = filtered_vouchers.filter(file__category__name=q)
        except:
            pass

    start = (page - 1) * page_size
    end = start + page_size

    total_vouchers = filtered_vouchers.count()
    has_more = total_vouchers > end

    vouchers_page = filtered_vouchers[start:end]

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string(
            'vouchers/partials/voucher_items.html',
            {'vouchers': vouchers_page}
        )

        return JsonResponse({
            'html': html,
            'has_more': has_more,
            'next_page': page + 1 if has_more else None
        })

    return render(request, 'vouchers/vouchers_list.html', {
        'has_more': has_more,
        'next_page': page + 1 if has_more else None,
        'vouchers': vouchers_page,
        'categories': categories,
        'current_status': status_filter
    })


@login_required(login_url='/users/login/')
def addCategory(request):
    if request.method == 'POST':
        category_name = request.POST.get('name', '').strip()
        
        if not category_name:
            messages.warning(request, 'Category name is required')
            return redirect('vouchers:voucherFiles')
            
        if VoucherCategory.objects.filter(name=category_name).exists():
            messages.warning(request, 'Category already exists')
            return redirect('vouchers:voucherFiles')
            
        new_category = VoucherCategory(name=category_name)
        new_category.save()
        
        voucher_log = VoucherLogs(
            user=request.user,
            action=f"{request.user.username} created category {category_name}",
            action_type='create',
            ip_address=get_client_ip(request)
        )
        voucher_log.save()
        
        messages.success(request, 'Category successfully added')
    
    return redirect('vouchers:voucherFiles')


@login_required(login_url='/users/login/')    
def populateVouchers(request, pk):
    files = VoucherFile.objects.all()
    
    try:
        file = VoucherFile.objects.get(pk=pk)
    except VoucherFile.DoesNotExist:
        messages.error(request, 'Voucher file not found')
        return redirect('vouchers:voucherFiles')

    if file.status != 'not populated':
        messages.error(request, "File is already populated")
        return redirect('vouchers:voucherFiles')

    try:
        voucher_count = 0
        with open(file.file.path, "r") as f:
            lines = f.readlines()
            
            for line in lines[7:]:
                voucher_code = line.strip()
                if voucher_code:
                    if not Vouchers.objects.filter(voucher_no=voucher_code).exists():
                        voucher = Vouchers(
                            user=request.user,
                            voucher_no=voucher_code,
                            file=file,
                            validity_duration=24,
                        )
                        voucher.save()
                        voucher_count += 1
        
        file.status = 'populated'
        file.save()
        
        voucher_log = VoucherLogs(
            user=request.user,
            action=f"{request.user.username} populated {voucher_count} vouchers from {file.name}",
            action_type='populate',
            ip_address=get_client_ip(request)
        )
        voucher_log.save()
        
        messages.success(request, f"Successfully populated {voucher_count} vouchers")
        
        if request.POST.get('sync_to_pfsense') == 'yes':
            return redirect('vouchers:syncToPfsense', pk=pk)
        
        return redirect('vouchers:vouchersList')
        
    except Exception as e:
        logger.error(f"Error populating vouchers: {str(e)}")
        messages.error(request, f"Error populating vouchers: {str(e)}")
        return redirect('vouchers:voucherFiles')


@login_required(login_url='/users/login/')
def syncToPfsense(request, pk=None):
    pass


@login_required(login_url='/users/login/')
def addVoucherUser(request, pk):
    voucher_users = VoucherUser.objects.all()
    
    try:
        voucher = Vouchers.objects.get(id=pk)
    except Vouchers.DoesNotExist:
        messages.error(request, 'Voucher not found')
        return redirect('vouchers:vouchersList')
    
    if hasattr(voucher, 'voucher_user'):
        messages.warning(request, 'This voucher already has a user assigned')
        return redirect('vouchers:printVoucher', pk=pk)
    
    form = VoucherUserForm()
    
    if request.method == 'POST':
        form = VoucherUserForm(request.POST)
        if form.is_valid():
            vu_object = form.save(commit=False)
            vu_object.voucher = voucher
            vu_object.voucher_no = voucher.voucher_no
            vu_object.save()
            
            voucher_log = VoucherLogs(
                user=request.user,
                action=f"{request.user.username} assigned voucher {voucher.voucher_no} to {vu_object.name}",
                action_type='create',
                voucher=voucher,
                ip_address=get_client_ip(request)
            )
            voucher_log.save()
            
            messages.success(request, 'User information saved successfully')
            return redirect('vouchers:printVoucher', voucher.id)
    
    return render(request, 'vouchers/addVoucherUser.html', {
        'form': form,
        'voucher': voucher,
        'voucher_users': voucher_users
    })


@login_required(login_url='/users/login/') 
def printVoucher(request, pk):
    try:
        voucher = Vouchers.objects.get(pk=pk) 
    except Vouchers.DoesNotExist:
        messages.error(request, 'Voucher not found')
        return redirect('vouchers:vouchersList')
    
    if request.method == 'POST':
        status = request.POST.get('status', '')
        if status in ['printed', 'used']:
            voucher.status = status
            
            if status == 'printed' and not voucher.date_printed:
                voucher.date_printed = timezone.now()
            
            voucher.save()
            
            voucher_log = VoucherLogs(
                user=request.user,
                action=f"{request.user.username} marked voucher {voucher.voucher_no} as {status} ({voucher.file.category.name})",
                action_type='print' if status == 'printed' else 'use',
                voucher=voucher,
                ip_address=get_client_ip(request)
            )
            voucher_log.save()
            
            messages.success(request, f'Voucher marked as {status}')
            return redirect('vouchers:vouchersList')
    
    return render(request, 'vouchers/printVoucher.html', {'voucher': voucher})


@login_required(login_url='/users/login/')
def voucherLog(request):
    page = int(request.GET.get('page', 1))
    page_size = 20  
    q = request.GET.get('q', '')
    
    logs = VoucherLogs.objects.all().select_related('user', 'voucher')

    if q in ['create', 'print', 'populate', 'use', 'sync', 'expire']:
        logs = logs.filter(action_type=q)
    elif q: 
        logs = logs.filter(
            Q(user__username__icontains=q) |
            Q(action__icontains=q)
        )
    
    start = (page - 1) * page_size
    end = start + page_size
    
    total_logs = logs.count()
    has_more = total_logs > end
    
    logs_page = logs[start:end]
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest': 
        html = render_to_string(
            'vouchers/partials/log_items.html', 
            {'logs': logs_page}
        )
        
        return JsonResponse({
            'html': html,
            'has_more': has_more,
            'next_page': page + 1 if has_more else None
        })
    
    return render(request, 'vouchers/voucherLogs.html', {
        'logs': logs_page,
        'has_more': has_more,
        'next_page': page + 1 if has_more else None,
        'current_filter': q
    })


@login_required(login_url='/users/login/')
def checkVoucherStatus(request, voucher_no):
    try:
        voucher = Vouchers.objects.get(voucher_no=voucher_no)
        
        data = {
            'success': True,
            'voucher_no': voucher.voucher_no,
            'status': voucher.status,
            'active': voucher.active,
            'validity_duration': voucher.validity_duration,
            'expiry_time': voucher.expiry_time.isoformat() if voucher.expiry_time else None,
            'category': voucher.file.category.name,
            'date_created': voucher.date_created.isoformat(),
            'date_used': voucher.date_used.isoformat() if voucher.date_used else None,
            'date_printed': voucher.date_printed.isoformat() if voucher.date_printed else None,
        }
        
        if hasattr(voucher, 'voucher_user'):
            data['user'] = {
                'name': voucher.voucher_user.name,
                'phone': voucher.voucher_user.phonenumber,
                'email': voucher.voucher_user.email,
            }
        
        return JsonResponse(data)
        
    except Vouchers.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Voucher not found'
        }, status=404)