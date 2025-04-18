from celery import shared_task
from django.core.mail import send_mail
from django.utils.timezone import now, timedelta
from .models import Installment

@shared_task
def send_due_reminders(days_before_due=3):
    due_date = now().date() + timedelta(days=days_before_due)
    installments = Installment.objects.filter(due_date=due_date, status='due')
    
    for installment in installments:
        customer = installment.customer
        if customer.email:
            send_mail(
                subject="Installment Due Reminder",
                message=f"Dear {customer.username},\n\nYou have an installment of {installment.due_amount} due on {installment.due_date}. Please make sure to pay on time to avoid penalties.",
                from_email=None,  
                fail_silently=False,
            )
            print(f"Reminder email sent to {customer.email} for installment due on {installment.due_date}")

    return f"Reminder emails sent for installments due on {due_date}"

@shared_task
def test_task():
    print(">>> Celery is working fine!")
    # send_mail(
    #         subject="Your OTP Code",
    #         message=f"Your OTP code is 1234",
    #         from_email=from_email,
    #         recipient_list=['tonniahmedhstustat19@gmail.com'],
    #         fail_silently=False,
    #     )
    # print(">>> Email sent successfully!")
    return "Done"
