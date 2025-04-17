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

    def validate_amount(self, value):
        installment = self.context.get('installment')
        if not installment:
            raise serializers.ValidationError("Installment context not provided.")
        
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive.")
        
        if value > installment.due_amount:
            raise serializers.ValidationError(f"Payment cannot exceed the due amount ({installment.due_amount}).")
        
        return value