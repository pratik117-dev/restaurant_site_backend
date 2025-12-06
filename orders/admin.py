from django.contrib import admin
from .models import CustomUser, MenuItem, Order

from django import forms
from django.utils.html import format_html
from .models import MenuItem, DeliveryStatus
from cloudinary.forms import CloudinaryFileField


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['email', 'name', 'is_admin', 'is_staff', 'is_active']



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


class MenuItemAdminForm(forms.ModelForm):
    """Custom form to properly handle CloudinaryField in admin"""
    image = CloudinaryFileField(
        options={
            'folder': 'menu_images/',
            'resource_type': 'image',
        },
        required=False
    )
    
    class Meta:
        model = MenuItem
        fields = '__all__'

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    form = MenuItemAdminForm
    list_display = ['name', 'category', 'price', 'image_thumbnail']
    list_filter = ['category']
    search_fields = ['name', 'description']
    
    def image_thumbnail(self, obj):
        """Display small thumbnail in list view"""
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return "No image"
    
    image_thumbnail.short_description = 'Preview'
    
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        """Display larger image in detail view"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 300px; border-radius: 8px;" />',
                obj.image.url
            )
        return "No image uploaded yet"
    
    image_preview.short_description = 'Current Image'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'category')
        }),
        ('Pricing', {
            'fields': ('price',)
        }),
        ('Image', {
            'fields': ('image_preview', 'image'),
            'description': 'Upload a new image or keep the existing one'
        }),
    )


@admin.register(DeliveryStatus)
class DeliveryStatusAdmin(admin.ModelAdmin):
    list_display = ['available', 'updated_at']
    readonly_fields = ['updated_at']
    
    def has_add_permission(self, request):
        return not DeliveryStatus.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False