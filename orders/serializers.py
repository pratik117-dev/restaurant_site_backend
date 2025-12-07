from rest_framework import serializers
from .models import CustomUser, MenuItem, Order, DeliveryStatus, OTP
from django.utils import timezone
from datetime import timedelta

# -------------------
# User & Registration
# -------------------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'name', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Create inactive user only
        user = CustomUser.objects.create(
            email=validated_data['email'],
            name=validated_data['name'],
            is_active=False
        )
        return user

# Serializer to verify OTP
class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        email = data['email']
        otp_input = data['otp']

        try:
            otp_obj = OTP.objects.get(user__email=email)
        except OTP.DoesNotExist:
            raise serializers.ValidationError("Invalid email or OTP.")

        # Check expiration
        if timezone.now() > otp_obj.created_at + timedelta(minutes=10):
            otp_obj.delete()
            raise serializers.ValidationError("OTP expired.")

        if otp_obj.otp != otp_input:
            raise serializers.ValidationError("Incorrect OTP.")

        data['otp_obj'] = otp_obj
        return data

    def save(self):
        otp_obj = self.validated_data['otp_obj']
        user = otp_obj.user

        # Activate user and set password
        user.is_active = True
        user.set_password(otp_obj.raw_password)
        user.save()

        # Delete OTP after use
        otp_obj.delete()

        return user

# Optional: Resend OTP serializer
class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = CustomUser.objects.get(email=value, is_active=False)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User not found or already active.")
        self.user = user
        return value

    def save(self):
        import random
        from django.core.mail import send_mail

        # Delete old OTP
        OTP.objects.filter(user=self.user).delete()

        # Create new OTP
        otp_code = str(random.randint(100000, 999999))
        OTP.objects.create(user=self.user, otp=otp_code, raw_password=self.user.password)

        # Send OTP email
        send_mail(
            subject="Your OTP Code",
            message=f"Your OTP is: {otp_code}",
            from_email=None,
            recipient_list=[self.user.email],
            fail_silently=False,
        )

        return otp_code

# -------------------
# Login Serializer
# -------------------
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

# -------------------
# Menu, Orders, Delivery Status (unchanged)
# -------------------
class MenuItemSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'description', 'price', 'image', 'image_url', 'category']
        extra_kwargs = {'image': {'write_only': True}}
    
    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None

class OrderSerializer(serializers.ModelSerializer):
    items = MenuItemSerializer(many=True, read_only=True)
    items_ids = serializers.PrimaryKeyRelatedField(queryset=MenuItem.objects.all(), many=True, write_only=True, source='items')
    user_name = serializers.CharField(source='user.name', read_only=True, default='Unknown')
    delivery_charge = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'user', 'user_name', 'items', 'items_ids', 'status', 'total_price', 'created_at', 'phone', 'location', 'delivery_charge', 'items_data']
        read_only_fields = ['user', 'status', 'total_price', 'created_at']

    def get_delivery_charge(self, obj):
        return 50.00

    def to_representation(self, instance):
        data = super().to_representation(instance)
        items_data = instance.items_data
        if items_data:
            data['items'] = [
                {**item, 'quantity': next((i['quantity'] for i in items_data if i['id'] == item['id']), 1), 'price': next((i['price'] for i in items_data if i['id'] == item['id']), item['price'])}
                for item in data['items']
            ]
        return data

class AdminOrderSerializer(serializers.ModelSerializer):
    items = MenuItemSerializer(many=True, read_only=True)
    items_ids = serializers.PrimaryKeyRelatedField(queryset=MenuItem.objects.all(), many=True, write_only=True, source='items')

    class Meta:
        model = Order
        fields = ['id', 'user', 'items', 'items_ids', 'status', 'total_price', 'created_at', 'phone', 'location']
        read_only_fields = ['user', 'total_price', 'created_at']

class DeliveryStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryStatus
        fields = ['available', 'updated_at']
