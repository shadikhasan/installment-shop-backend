from rest_framework import serializers
from .models import Product, Purchase, Installment
from accounts.models import Customer


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class PurchaseSerializer(serializers.ModelSerializer):
    customer = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Purchase
        fields = '__all__'
        read_only_fields = ['total_price']


class InstallmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Installment
        fields = '__all__'
        read_only_fields = ['due_amount', 'status', 'due_date', 'payment_date']


class InstallmentPaySerializer(serializers.Serializer):
    paid_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
