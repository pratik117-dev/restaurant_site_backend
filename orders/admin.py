from django.contrib import admin
from .models import CustomUser, MenuItem, Order

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['email', 'name', 'is_admin', 'is_staff', 'is_active']

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category', 'image']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'total_price', 'phone', 'location', 'created_at']
    list_editable = ['status']  # Makes status editable directly in the list view (dropdown)
    list_filter = ['status', 'created_at']  # Add filters for status and creation date
    search_fields = ['user__email', 'id']  # Search by user email or order ID
    readonly_fields = ['id', 'user', 'items', 'total_price', 'created_at']  # Prevent editing these fields
    fieldsets = (
        (None, {
            'fields': ('user', 'items', 'status', 'total_price', 'phone', 'location', 'created_at')
        }),
    )

# Removed duplicate registrations: admin.site.register(CustomUser, CustomUserAdmin), etc.
# The @admin.register decorators handle registration automatically.
