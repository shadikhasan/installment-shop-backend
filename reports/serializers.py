from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.models import Sum
from myapp.models import Purchase, Installment
from myapp.serializers import PurchaseSerializer  # Your existing serializer

User = get_user_model()

from datetime import timedelta
from django.utils import timezone

from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum
from myapp.models import Purchase, Installment

class UserPaymentSummarySerializer(serializers.ModelSerializer):
    total_paid_amount = serializers.SerializerMethodField()
    total_due_amount = serializers.SerializerMethodField()
    total_purchase_count = serializers.SerializerMethodField()
    total_product_quantity = serializers.SerializerMethodField()
    total_installment_count = serializers.SerializerMethodField()
    fully_paid_purchases = serializers.SerializerMethodField()
    due_purchases = serializers.SerializerMethodField()
    overall_status = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'total_paid_amount',
            'total_due_amount',
            'total_purchase_count',
            'total_product_quantity',
            'total_installment_count',
            'fully_paid_purchases',
            'due_purchases',
            'overall_status',
        ]

    def _filter_by_range(self, queryset, date_field='purchase_date'):
        """Helper method to filter based on weekly/monthly range."""
        filter_range = self.context.get("range")
        now = timezone.now()

        if filter_range == 'weekly':
            start = now - timedelta(days=7)
            return queryset.filter(**{f"{date_field}__gte": start})
        elif filter_range == 'monthly':
            start = now - timedelta(days=30)
            return queryset.filter(**{f"{date_field}__gte": start})
        return queryset  # If no range is provided, no filtering applied

    def get_total_paid_amount(self, user):
        qs = Installment.objects.filter(purchase__customer=user)
        qs = self._filter_by_range(qs, date_field='payment_date')  # Filter by payment date
        return qs.aggregate(total_paid=Sum('paid_amount'))['total_paid'] or 0

    def get_total_due_amount(self, user):
        qs = Installment.objects.filter(purchase__customer=user)
        qs = self._filter_by_range(qs, date_field='due_date')  # Filter by due date
        return qs.aggregate(total_due=Sum('due_amount'))['total_due'] or 0

    def get_total_purchase_count(self, user):
        qs = Purchase.objects.filter(customer=user)
        qs = self._filter_by_range(qs, date_field='purchase_date')  # Filter purchases by date range
        return qs.count()

    def get_total_product_quantity(self, user):
        qs = Purchase.objects.filter(customer=user)
        qs = self._filter_by_range(qs, date_field='purchase_date')  # Filter purchases by date range
        return qs.aggregate(total_qty=Sum('quantity'))['total_qty'] or 0

    def get_total_installment_count(self, user):
        qs = Installment.objects.filter(purchase__customer=user)
        qs = self._filter_by_range(qs, date_field='due_date')  # Filter installments by due date
        return qs.count()

    def get_fully_paid_purchases(self, user):
        qs = Purchase.objects.filter(customer=user, status='paid')
        qs = self._filter_by_range(qs, date_field='purchase_date')  # Filter purchases by date range
        return qs.count()

    def get_due_purchases(self, user):
        qs = Purchase.objects.filter(customer=user, status='due')
        qs = self._filter_by_range(qs, date_field='purchase_date')  # Filter purchases by date range
        return qs.count()

    def get_overall_status(self, user):
        purchases = Purchase.objects.filter(customer=user)
        purchases = self._filter_by_range(purchases, date_field='purchase_date')  # Filter purchases by date range
        if not purchases.exists():
            return 'n/a'
        if purchases.filter(status='due').exists():
            return 'due'
        return 'paid'



