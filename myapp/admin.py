from django.contrib import admin
from .models import  Product, Purchase, Installment

# Register Customer model
# Register Product model
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Product._meta.fields]  # Display these fields in the list view
    search_fields = ('name', 'description')  # Search functionality

# Register Purchase model
@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'customer', 'product', 'quantity', 'purchase_date',
        'total_price', 'first_installment_amount', 'installment_count', 'status'
    ]
    list_select_related = ('customer', 'product')
    search_fields = ('customer__username', 'customer__email', 'product__name')
    list_filter = ('purchase_date', 'installment_count', 'status')
    date_hierarchy = 'purchase_date'
    ordering = ('-purchase_date',)

    

# Register Installment model
@admin.register(Installment)
class InstallmentAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Installment._meta.fields]
    search_fields = ('purchase__customer__username', 'purchase__product__name')
    list_filter = ('status',)
    readonly_fields = ['due_amount', 'due_date', 'status', 'payment_date']  # Making these fields read-only
