from vouchers.models import VoucherFile, Vouchers, VoucherCategory, VoucherLogs, VoucherUser
from django.db.models import Q
from django.contrib import messages
from .serializers import *
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required 
from vouchers.forms import AddVoucherFileForm, VoucherUserForm
import csv
from django.shortcuts import render, redirect, get_object_or_404
from loguru import logger

@login_required(login_url='/users/login/')
def voucherFiles(request):
    files = VoucherFile.objects.all()
    form = AddVoucherFileForm()
    if request.method == 'POST':
        form = AddVoucherFileForm(request.POST, request.FILES)
        if form.is_valid():
            voucher_object = form.save(commit = False)
            voucher_object.user = request.user
            voucher_log = VoucherLogs(
                user = request.user,
                action = f"{request.user} created {request.POST['name']}"
            )
            voucher_object.save()
            voucher_log.save()

    return render(request, 'vouchers/vouchers.html', {
        'voucherFiles': files,
        'form': form
    })

@login_required(login_url='/users/login/')
def vouchersList(request):
    vou = Vouchers.objects.all()
    categories = VoucherCategory.objects.all()
    q =  request.GET.get('q') if request.GET.get('q') != None else ''
    try:
        filtered_vouchers = vou.filter(file__category = q) & vou.filter(status = 'unused')
    except:
        filtered_vouchers = vou.all() & vou.filter(status = 'unused')

    return render(request, 'vouchers/vouchers_list.html', {
        'vouchers': filtered_vouchers,
        'categories':categories
    })

@login_required(login_url='/users/login/')
def addCategory(request):
    if request.method  == 'POST':
        print(request.POST['name'])
        category_name = request.POST['name']
        if VoucherCategory.objects.filter(name = category_name).exists():
            messages.warning(request, 'category exists')
            return redirect('vouchers:voucherFiles')
        new_category = VoucherCategory(
            name = category_name
        )
        new_category.save()
    messages.success(request, 'category successfully added')
    return redirect('vouchers:voucherFiles')

@login_required(login_url='/users/login/')
def populateVouchers(request, pk):
    files = VoucherFile.objects.all()
    
    file = get_object_or_404(VoucherFile, pk=pk)

    if file.status == 'populated':
        messages.error(request, "File is already populated")
        return redirect('vouchers:voucherList')

    file_path = f'staticfiles/media/{file.file}'
   
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)  

            row_count = 1

            logger.info(f'Processing file: {file}')

            vouchers_to_create = []  
            for row in reader:
                logger.info(f'processing row {row_count}')
                voucher = Vouchers(
                    user=request.user,
                    voucher_username=row["username"],  
                    voucher_password=row["password"],  
                    file=file,
                    status='unused'
                )
                vouchers_to_create.append(voucher)
                row_count += 1
            
            Vouchers.objects.bulk_create(vouchers_to_create)

            VoucherLogs.objects.create(
                user=request.user,
                action=f"{request.user} populated {file.name}"
            )
            file.status = 'populated'
            file.save()

            messages.success(request, "Vouchers Successfully Populated.")
            return redirect('vouchers:voucherList')

    except Exception as e:
        messages.error(request, f"Error processing file: {str(e)}")

    return render(request, 'vouchers/vouchers.html', {'voucherFiles': files})


@login_required(login_url='/users/login/')
def addVoucherUser(request, pk):
    voucher_users = VoucherUser.objects.all()
    try:
        voucher = Vouchers.objects.get(id = pk)
    except:
        return render(request, '404.html')
    form =  VoucherUserForm()
    if request.method == 'POST':
        form =  VoucherUserForm(request.POST)
        if form.is_valid():
            vu_object = form.save(commit = False)
            vu_object.voucher_no = voucher.voucher_no,
            vu_object.save()
            return redirect('vouchers:printVoucher', voucher.id)
    return render(request, 'vouchers/addVoucherUser.html', {
        'form':form,
        'voucher_users':voucher_users
    })

@login_required(login_url='/users/login/') 
def printVoucher(request, pk):
    try:
        voucher = Vouchers.objects.get(pk=pk) 
    except:
        return render(request, '404.html')
    
    if request.method == 'POST':
        if request.POST['status'] != '':
            voucher.status = request.POST['status']
            voucher_log = VoucherLogs(
                user = request.user,
                action = f"{request.user} printed voucher {voucher.voucher_no} ({voucher.file.category.name})"
            )
            voucher.save()
            voucher_log.save()
            return redirect('vouchers:voucherList')
    return render(request, 'vouchers/printVoucher.html', {'voucher':voucher})

@login_required(login_url='/users/login/')
def voucherLog(request):
    logs = VoucherLogs.objects.all()
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    if q == 'create':
        return render(request, 'vouchers/voucherLogs.html', {
            'logs': logs.filter(Q(action__icontains = q ))
        })
    elif q == 'print':
        return render(request, 'vouchers/voucherLogs.html', {
            'logs': logs.filter(Q(action__icontains = q ))
        })
    elif q == 'populate':
        return render(request, 'vouchers/voucherLogs.html', {
            'logs': logs.filter(Q(action__icontains = q ))
        })
    
    return render(request, 'vouchers/voucherLogs.html',
        {'logs': logs or VoucherLogs.objects.filter(
            Q(user__username__icontains = q) |
            Q(action__icontains = q)|
            Q(date_created__icontains = q)
        )}
    )