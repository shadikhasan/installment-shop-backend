from django.db import models
from django.forms import ValidationError
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class Purchase(models.Model):
    STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('due', 'Due'),
    ]

    customer = models.ForeignKey('accounts.Customer', on_delete=models.CASCADE, related_name='purchases')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='purchases')
    quantity = models.PositiveIntegerField(default=1)
    purchase_date = models.DateTimeField(default=timezone.now)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    first_installment_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    installment_count = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='due', editable=False)

    def clean(self):
        # Ensure necessary fields are not None
        if self.product and self.quantity and self.first_installment_amount is not None:
            temp_total_price = self.product.price * self.quantity
            expected_min_first_installment = temp_total_price * Decimal('0.30')

            if self.first_installment_amount < expected_min_first_installment:
                raise ValidationError(
                    f"First installment must be at least 30% of total price ({expected_min_first_installment:.2f})."
                )
            if self.first_installment_amount > temp_total_price:
                raise ValidationError("First installment cannot exceed total price.")
            if self.installment_count < 1:
                raise ValidationError("Installment count must be at least 1.")

        
    def save(self, *args, **kwargs):
        if self.product and self.quantity:
            self.total_price = self.product.price * self.quantity
        self.full_clean()  # includes clean()
        super().save(*args, **kwargs)

    
    def __str__(self):
        return f'{self.customer.email} - {self.product.name} x {self.quantity}'


class Installment(models.Model):
    STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('due', 'Due'),
    ]

    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='installments')
    installment_number = models.PositiveIntegerField()
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    due_amount = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    due_date = models.DateTimeField()  # No default anymore
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, editable=False, default='due')
    payment_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.purchase.product.name} - Installment {self.installment_number} ({self.status})'

    def clean(self):
        if self.first_installment_amount > self.total_price:
            raise ValidationError("First installment can't exceed total price.")
        if self.installment_count < 1:
            raise ValidationError("Installment count must be at least 1.")

