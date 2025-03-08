import os
from .models import Sale
from django.core.mail import send_mail, send_mass_mail
from celery import shared_task
from django.template.loader import get_template
from django.core.mail import EmailMessage
from django.conf import settings
from xhtml2pdf import pisa
from io import BytesIO
from datetime import date
from .models import EndOfDay, Sale
from loguru import logger
from django.core.files import File
import datetime
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


@shared_task
def generate_eod_pdf(eod_id):
    """
        Generate End of Day PDF report using xhtml2pdf
    """

    eod = EndOfDay.objects.filter(id=eod_id).first()
    logger.info(eod)
    sales_data = Sale.objects.filter(date__date=datetime.date.today()).select_related(
        'cashier',
        'client'
    )

    today = date.today().strftime('%Y-%m-%d')
    filename = f"eod_report_{today}.pdf"
    file_path = os.path.join(settings.MEDIA_ROOT, 'eod_reports', filename)
    
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    total_sales = sum(sale.amount for sale in sales_data)
    total_items = len(sales_data)
    
    context = {
        'sales': sales_data,
        'date': today,
        'total_sales': total_sales,
        'total_items': total_items,
    }
    
    template = get_template('end_of_day/end_of_day_report_template.html') 
    html = template.render(context)
    result_file = open(file_path, "w+b")
    pisa_status = pisa.CreatePDF(html, dest=result_file)
    result_file.close()
    
    if pisa_status.err:
        return None
    
    with open(file_path, "rb") as pdf_file:
        eod.pdf.save(filename, File(pdf_file), save=True)
    
    return file_path


@shared_task
def send_eod_email(eod_id):
    """
    Send End of Day report via email using HTML template
    """
    try:
        eod = EndOfDay.objects.get(id=eod_id)
        sales = Sale.objects.filter(date__date=datetime.date.today()).select_related(
            'cashier',
            'client'
        )

        today = date.today().strftime('%Y-%m-%d')
        current_year = date.today().year
        
        reports_dir = os.path.join(settings.MEDIA_ROOT, 'eod_reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        pdf_filename = f"eod_report_{today}.pdf"
        pdf_path = os.path.join(reports_dir, pdf_filename)
        
        if not os.path.exists(pdf_path):
            pdf_path = generate_eod_pdf(eod)
        
        # dashboard_url = f"{settings.BASE_URL}/end-of-day/{eod.id}/"

        # sales categories totals 
        sale_totals = {
            category: sum(sale.amount for sale in sales if sale.sale_type== category)
            for category in {sale.sale_type for sale in sales}
        }
        
        context = {
            'eod': eod,
            'sales':sales,
            'date': today,
            'year': current_year,
            'sales_cat_totals':sale_totals
            # 'dashboard_url': dashboard_url
        }
        
        html_message = render_to_string('emails/eod_report_email.html', context)
        plain_message = strip_tags(html_message)
        
        subject = f"End of Day Report - {today}"
        from_email = "admin@techcity.co.zw"
        recipient_list = ['cassy@email.com']
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=from_email,
            to=recipient_list
        )
        email.attach_alternative(html_message, "text/html")
        
        with open(pdf_path, 'rb') as f:
            email.attach(pdf_filename, f.read(), 'application/pdf')
    
        email.send()
        
        logger.info(f"EOD report email sent successfully for {today}")
        return True
    
    except EndOfDay.DoesNotExist:
        logger.error(f"EOD with ID {eod_id} not found")
        return False
    except Exception as e:
        logger.error(f"Error sending EOD email: {str(e)}")
        return False