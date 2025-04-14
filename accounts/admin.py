from django.contrib import admin

from accounts.models import Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_verified', 'date_joined')  # Display these fields in the list view
    search_fields = ('username', 'email', 'first_name', 'last_name')  # Search functionality
    list_filter = ('is_verified', 'date_joined')  # Filter by is_verified and date_joined

