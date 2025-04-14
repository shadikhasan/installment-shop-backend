from datetime import timedelta
from decimal import Decimal
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.db import models
from accounts.models import Customer


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class Purchase(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='purchases')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='purchases')
    quantity = models.PositiveIntegerField(default=1)
    purchase_date = models.DateTimeField(default=timezone.now)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    first_installment_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    installment_count = models.PositiveIntegerField()
    
    def clean(self):
        if self.installment_count > 2:
            raise ValidationError("Installment count cannot be more than 2.")


    def __str__(self):
        return f'{self.customer.email} - {self.product.name} x {self.quantity}'

    def save(self, *args, **kwargs):
        self.total_price = self.product.price * self.quantity
        super().save(*args, **kwargs)

    @property
    def remaining_installment_amount(self):
        """Total remaining amount after the first installment."""
        return self.total_price - self.first_installment_amount
    @property
    def remaining_amount_per_installment(self):
        """Each remaining installment amount, evenly split."""
        if self.installment_count > 1:
            return self.remaining_installment_amount / (self.installment_count - 1)
        return 0


class Installment(models.Model):
    
    STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('due', 'Due'),
    ]
    
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='installments')
    installment_number = models.PositiveIntegerField()
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    due_amount = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    due_date = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, editable=False, default='due')
    payment_date = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Calculate due_amount and due_date based on installment number
        if self.installment_number == 1:
            self.due_amount = self.purchase.remaining_installment_amount
            self.due_date = self.purchase.purchase_date
        else:
            self.due_amount = self.purchase.total_price - (self.purchase.first_installment_amount + self.paid_amount)
            self.due_date = self.purchase.purchase_date + timedelta(days=30 * (self.installment_number - 1))

        # Update status based on the paid_amount
        if self.due_amount == 0:
            self.status = 'paid'
            if not self.payment_date:
                self.payment_date = timezone.now()  # Set payment date when paid
        else:
            self.status = 'due'
            self.payment_date = None  # Reset payment date if not fully paid
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.purchase.product.name} - Installment {self.installment_number} ({self.status})'
