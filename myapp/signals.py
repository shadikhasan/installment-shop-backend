from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal
from datetime import timedelta
from .models import Purchase, Installment

@receiver(post_save, sender=Purchase)
def create_installments(sender, instance, created, **kwargs):
    print("✅ Signal triggered for Purchase:", instance.id)

    # 🔒 Prevent duplicate installments if already created
    if not created or Installment.objects.filter(purchase=instance).exists():
        print("⚠️ Skipping signal: Installments already exist or this isn't a new purchase.")
        return

    # Step 1: First installment (paid)
    Installment.objects.create(
        purchase=instance,
        installment_number=1,  # Changed from 0 → 1 for consistency
        paid_amount=instance.first_installment_amount,
        due_amount=Decimal('0.00'),
        due_date=instance.purchase_date,
        payment_date=instance.purchase_date,
        status='paid'
    )

    # Step 2: Remaining installments (due)
    remaining_balance = instance.total_price - instance.first_installment_amount
    if instance.installment_count > 1:
        per_installment = (remaining_balance / (instance.installment_count - 1)).quantize(Decimal('0.01'))

        for i in range(2, instance.installment_count + 1):
            due_date = instance.purchase_date + timedelta(days=30 * (i - 1))
            Installment.objects.create(
                purchase=instance,
                installment_number=i,
                paid_amount=Decimal('0.00'),
                due_amount=per_installment,
                due_date=due_date,
                status='due'
            )
