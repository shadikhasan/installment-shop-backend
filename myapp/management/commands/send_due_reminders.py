# your_app/management/commands/send_due_reminders.py
from django.core.management.base import BaseCommand
from datetime import timedelta, date
from myapp.models import Installment
from myapp.tasks import send_due_reminder_email

class Command(BaseCommand):
    help = 'Send due reminders before N days'

    def handle(self, *args, **kwargs):
        n_days_before = 3  # or any value
        reminder_date = date.today() + timedelta(days=n_days_before)

        due_installments = Installment.objects.filter(due_date=reminder_date, status='due')

        for installment in due_installments:
            customer = installment.purchase.customer
            send_due_reminder_email.delay(
                customer.email,
                customer.username,
                installment.due_date,
                installment.due_amount
            )
        self.stdout.write(self.style.SUCCESS(f"Sent reminders for {due_installments.count()} due installments."))
