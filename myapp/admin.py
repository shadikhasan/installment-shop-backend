from django.contrib import admin
from .models import Customer, Product, Purchase, Installment

# Register Customer model
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_verified', 'date_joined')  # Display these fields in the list view
    search_fields = ('username', 'email', 'first_name', 'last_name')  # Search functionality
    list_filter = ('is_verified', 'date_joined')  # Filter by is_verified and date_joined

# Register Product model
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Product._meta.fields]  # Display these fields in the list view
    search_fields = ('name', 'description')  # Search functionality

# Register Purchase model
@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'customer',
        'product',
        'quantity',
        'total_price',
        'first_installment_amount',
        'remaining_amount',
        'remaining_amount_per_installment',
        'installment_count',
        'purchase_date',
    )
    list_select_related = ('customer', 'product')
    search_fields = ('customer__username', 'customer__email', 'product__name')
    list_filter = ('purchase_date', 'installment_count')
    date_hierarchy = 'purchase_date'
    ordering = ('-purchase_date',)
    
    def remaining_amount(self, obj):
        return obj.remaining_installment_amount
    remaining_amount.short_description = 'Remaining Amount'

# Register Installment model
@admin.register(Installment)
class InstallmentAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Installment._meta.fields]
    search_fields = ('purchase__customer__username', 'purchase__product__name')
    list_filter = ('status',)
    readonly_fields = ['due_amount', 'due_date', 'status', 'payment_date']  # Making these fields read-only
