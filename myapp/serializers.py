from datetime import datetime
from django.utils import timezone
from decimal import Decimal
from rest_framework import serializers
from .models import Product, Purchase, Installment
from accounts.models import Customer


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class PurchaseSerializer(serializers.ModelSerializer):
    customer = serializers.HiddenField(default=serializers.CurrentUserDefault())
    product_name = serializers.CharField(source='product.name', read_only=True)
    class Meta:
        model = Purchase
        fields = '__all__'
        read_only_fields = ['total_price']
        
    def validate_installment_count(self, value):
        if value < 1:
            print("error: Installment count cannot be less than 1.")
            raise serializers.ValidationError("Installment count cannot be less than 1.")
        return value
    
    def validate_first_installment_amount(self, value):
        if value < 1:
            print("error: First Installment Amount can not less than 1.")
            raise serializers.ValidationError("First Installment Amount can not less than 1.")
        return value
    
    def validate(self, data):
        product = data.get('product')
        quantity = data.get('quantity', 1)
        first_installment_amount = data.get('first_installment_amount')
        installment_count = data.get('installment_count')

        if product and quantity and first_installment_amount is not None:
            total_price = product.price * quantity
            data['total_price'] = total_price  # assign it so it can be saved in model

            if installment_count == 1:
                if first_installment_amount != total_price:
                    raise serializers.ValidationError({
                        'first_installment_amount': "You must pay the full amount as first installment if only 1 installment is selected."
                    })
            else:
                expected_min = total_price * Decimal('0.30')
                if first_installment_amount < expected_min:
                    raise serializers.ValidationError({
                        'first_installment_amount': f"First installment must be at least 30% of total price (৳{expected_min:.2f})."
                    })
                if first_installment_amount > total_price:
                    raise serializers.ValidationError({
                        'first_installment_amount': "First installment cannot exceed total price."
                    })

        return data



    
class InstallmentSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    quantity = serializers.SerializerMethodField()

    class Meta:
        model = Installment
        fields = [
            'id',
            'product_name',
            'total_price',
            'quantity',
            'purchase',
            'installment_number',
            'paid_amount',
            'due_amount',
            'due_date',
            'status',
            'payment_date',
        ]
        read_only_fields = ['due_amount', 'status', 'due_date', 'payment_date']

    def get_product_name(self, obj):
        return obj.purchase.product.name

    def get_total_price(self, obj):
        return str(obj.purchase.total_price)

    def get_quantity(self, obj):
        return str(obj.purchase.quantity)

class PayInstallmentSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate(self, data):
        """Custom validation for late fees and overpayments."""
        installment = self.context['installment']
        amount = data['amount']

        is_late = timezone.now() > installment.due_date
        original_due = installment.due_amount
        penalty = Decimal('0.00')

        # If late, calculate 10% late fee
        if is_late:
            penalty = original_due * Decimal('0.10')
            total_due = original_due + penalty
            if amount < total_due:
                raise serializers.ValidationError(
                    f"Late payment! You must pay the full amount including penalty: ৳{total_due:.2f}"
                )
        else:
            total_due = original_due
        
        # Ensure that no overpayment is made
        if amount > total_due:
            raise serializers.ValidationError(
                f"You cannot pay more than the required amount: ৳{total_due:.2f}"
            )
        
        return data
    
    
