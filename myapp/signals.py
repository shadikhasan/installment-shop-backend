from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal
from datetime import timedelta

from .models import Purchase, Installment


@receiver(post_save, sender=Purchase)
def create_installments(sender, instance, created, **kwargs):
    if created:
        # Step 1: Create the first installment (paid)
        Installment.objects.create(
            purchase=instance,
            installment_number=0,
            paid_amount=instance.first_installment_amount,  # Customer paid amount
            due_amount=Decimal('0.00'),
            due_date=instance.purchase_date,
            payment_date=instance.purchase_date,
            status='paid'
        )

        # Step 2: Calculate remaining balance and per installment amount
        remaining_balance = instance.total_price - instance.first_installment_amount
        if instance.installment_count > 1:  # Avoid division by zero
            per_installment = (remaining_balance / (instance.installment_count - 1)).quantize(Decimal('0.01'))

            # Step 3: Create remaining installments (due)
            for i in range(1, instance.installment_count):
                due_date = instance.purchase_date + timedelta(days=30 * i)  # Set due date as 30 days apart
                
                # Create installment with due amount
                Installment.objects.create(
                    purchase=instance,
                    installment_number=i,
                    paid_amount=Decimal('0.00'),
                    due_amount=per_installment,
                    due_date=due_date,
                    status='due'
                )
