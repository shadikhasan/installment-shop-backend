from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
import random
from datetime import timedelta

from myapp.models import Product, Purchase, Installment
from accounts.models import Customer


class Command(BaseCommand):
    help = 'Generate 30 customers, 150 products, 100 purchases, and 150 installments'

    def handle(self, *args, **kwargs):
        # 1. Create 30 customers
        customer_count = Customer.objects.count()
        customers_needed = 30 - customer_count
        if customers_needed > 0:
            for i in range(customers_needed):
                idx = customer_count + i + 1
                email = f'testuser{idx}@example.com'
                Customer.objects.create_user(
                    username=f'testuser{idx}',
                    email=email,
                    password='password123',
                    is_verified=True
                )
            self.stdout.write(self.style.SUCCESS(f"Created {customers_needed} customers."))

        customers = list(Customer.objects.all()[:30])  # Use only 30

        # 2. Create 150 products
        for i in range(150):
            Product.objects.get_or_create(
                name=f'Product {i+1}',
                defaults={
                    'description': f'Description for product {i+1}',
                    'price': Decimal(random.randint(1000, 10000))
                }
            )
        products = list(Product.objects.all()[:150])

        self.stdout.write(self.style.SUCCESS("Created/ensured 150 products."))

        # 3. Create 100 purchases
        purchases = []
        for i in range(100):
            customer = random.choice(customers)
            product = random.choice(products)
            quantity = random.randint(1, 5)
            total_price = product.price * quantity
            first_installment = total_price * Decimal('0.35')
            installment_count = random.randint(1, 3)

            purchase = Purchase.objects.create(
                customer=customer,
                product=product,
                quantity=quantity,
                first_installment_amount=round(first_installment, 2),
                installment_count=installment_count
            )
            purchases.append((purchase, total_price - first_installment))

        self.stdout.write(self.style.SUCCESS("Created 100 purchases."))

        # 4. Create 150 installments
        total_installments_needed = 150
        created_installments = 0
        for purchase, remaining_amount in purchases:
            count = min(purchase.installment_count, total_installments_needed - created_installments)
            if count <= 0:
                break

            per_installment_amount = round(remaining_amount / count, 2)
            start_date = purchase.purchase_date + timedelta(days=30)

            for j in range(count):
                if created_installments >= total_installments_needed:
                    break

                due_date = start_date + timedelta(days=30 * j)
                paid = random.choice([True, False])
                late_fee = Decimal('0.00')

                if not paid and due_date < timezone.now():
                    late_fee = Decimal(random.randint(10, 100))

                Installment.objects.create(
                    purchase=purchase,
                    installment_number=j + 1,
                    due_amount=per_installment_amount,
                    due_date=due_date,
                    paid_amount=per_installment_amount if paid else Decimal('0.00'),
                    late_fee=late_fee,
                    status='paid' if paid else 'due',
                    payment_date=timezone.now() if paid else None,
                )
                created_installments += 1

        self.stdout.write(self.style.SUCCESS(f"Created {created_installments} installments."))
