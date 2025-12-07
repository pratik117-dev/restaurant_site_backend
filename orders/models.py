from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from decimal import Decimal

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from datetime import timedelta

from cloudinary.models import CloudinaryField

class CustomUserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, name, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
    objects = CustomUserManager()

    def __str__(self):
        return self.email

# class OTP(models.Model):
#     email = models.EmailField()
#     otp = models.CharField(max_length=6)
#     created_at = models.DateTimeField(auto_now_add=True)
#     name = models.CharField(max_length=100)
#     password = models.CharField(max_length=128)

#     def is_expired(self):
#         return timezone.now() > self.created_at + timedelta(minutes=10)

# Rest of the models (MenuItem, Order, OrderItem) remain the same

class MenuItem(models.Model):
    SIZE_CHOICES = [
        ('SMALL', 'Small'),
        ('MEDIUM', 'Medium'),
        ('LARGE', 'Large'),
    ]
    
    CATEGORY_CHOICES = [
        ('CHICKEN', 'Chicken'),
        ('VEG', 'Veg'),
        ('DRINKS', 'Drinks'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Base price
    
    # Use CloudinaryField with blank=True, null=True for admin compatibility
    image = CloudinaryField('image', folder='menu_images/', blank=True, null=True)
    
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='VEG')
    
    def __str__(self):
        return self.name
    
    @property
    def image_url(self):
        """Get the Cloudinary URL for the image"""
        if self.image:
            return self.image.url
        return None




class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('CANCELLED', 'Cancelled'),
        ('DELIVERYOUT', 'Out_for_delivery'),
        ('DELIVERED', 'Delivery_Success'),
        ('PAID', 'Paid'),
    ]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    items = models.ManyToManyField(MenuItem)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    phone = models.CharField(max_length=15, blank=True, null=True)  # Added
    location = models.TextField(blank=True, null=True)  # Added
    items_data = models.JSONField(default=list)  # Store quantities and prices


    def __str__(self):
        return f"Order {self.id} by {self.user.email}"
    



class CartItem(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='cart_items')
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('user', 'item')  # Prevent duplicates

    def __str__(self):
        return f"{self.item.name} x {self.quantity} ({self.user.email})"

    @property
    def total_price(self):
        return Decimal(self.item.price) * self.quantity


#delivery status
class DeliveryStatus(models.Model):
    available = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Delivery Status"
        verbose_name_plural = "Delivery Status"
    
    @classmethod
    def get_status(cls):
        status, created = cls.objects.get_or_create(id=1)
        return status