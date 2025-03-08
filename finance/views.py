from django.shortcuts import render, redirect
from django.http import JsonResponse
from . models import EndOfDay, EndOfDayItem
from django.template.loader import render_to_string
from django.db import transaction
import datetime
from finance.models import Sale
from .tasks import(
    send_eod_email,
    generate_eod_pdf
)
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404


@transaction.atomic
@login_required
def end_of_day(request):
    """
        Retrieves all the end of day objects with pagination (20 items per page)
        Returns JSON response for AJAX requests or renders the full template for direct access
    """
    if request.method == 'GET':
        page = int(request.GET.get('page', 1))
        query = request.GET.get('q', '')
        page_size = 20


        eod_list = EndOfDay.objects.all().order_by('-date')
        if query:
            eod_list = eod_list.filter(date__icontains=query)
    

        start = (page - 1) * page_size
        end = start + page_size
        
        paginated_eods = eod_list[start:end]
        total_eods = eod_list.count()
        has_more = total_eods > end
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            html = render_to_string(
                'end_of_day/partials/eod_items.html',
                {'end_of_day': paginated_eods}
            )
            
            return JsonResponse({
                'html': html,
                'has_more': has_more,
                'next_page': page + 1 if has_more else None
            })
        

        return render(request, 'end_of_day/end_of_day_list.html', {
            'eods': paginated_eods,
            'has_more': has_more,
            'next_page': page + 1 if has_more else None
        })
    

    if request.method == "POST":
        """
            Creates the end of day, sends email and creates the end_of_day pdf
        """
        try:
            with transaction.atomic():
                sales = Sale.objects.filter(date__date=datetime.date.today()).select_related(
                    'cashier',
                    'client'
                )

                eod = EndOfDay.objects.create(date=datetime.datetime.today(), amount=0)

                eod_items = []
                total_sales_amount = 0
                for sale in sales:
                    eod_items.append(
                        EndOfDayItem(
                            eod=eod,
                            sale=sale
                        )
                    )
                    total_sales_amount += sale.amount
                
                EndOfDayItem.objects.bulk_create(eod_items)
                eod.amount = total_sales_amount
                eod.save()

                generate_eod_pdf.delay(eod.id)
                send_eod_email.delay(eod.id)

                return redirect('finance:end_of_day')
            
        except Exception as e:
            return JsonResponse({'success':False, 'message':f'{e}'}, status=200)
        

@login_required
def eod_detail(request, id):
    try:
        data = list(EndOfDayItem.objects.filter(eod__id=id).values(
            'sale__sale_type',
            'sale__amount'
        ))
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'succes':False, 'message':f'{e}'}, status=400)
    


@login_required
def download_eod_pdf(requset, id):
    """
        Download pdf file for the eod
    """
    eod = get_object_or_404(EndOfDay, id=id)

    if eod.pdf:
        response = HttpResponse(eod.pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="End_of_day_{id}.pdf"'
        return response
    else:
        return HttpResponse("No PDF found for this delivery note.", status=404) 



            


