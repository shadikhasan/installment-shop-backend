from celery import shared_task
from django.core.mail import send_mail
from django.utils.timezone import now, timedelta
from accounts.models import Customer  # Adjust model import as needed
from .models import Installment

@shared_task
def send_due_reminders(days_before_due=3):
    due_date = now().date() + timedelta(days=days_before_due)
    installments = Installment.objects.filter(due_date=due_date, status='due')
    
    for installment in installments:
        customer = installment.customer
        if customer.email:
            send_mail(
                subject='Installment Due Reminder',
                message=f'Dear {customer.username},\n\nYou have an installment of amount {installment.due_amount} due on {installment.due_date}. Please make sure to pay on time to avoid penalties.',
                from_email='shadik.sk420@gmail.com',
                recipient_list=[customer.email],
            )

@shared_task
def test_task():
    print(">>> Celery is working fine!")
    return "Done"