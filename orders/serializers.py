from rest_framework import serializers
from .models import CustomUser, MenuItem, Order, DeliveryStatus

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'name', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    

class MenuItemSerializer(serializers.ModelSerializer):
    # This will return the full Cloudinary URL
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'description', 'price', 'image', 'image_url', 'category']
        extra_kwargs = {
            'image': {'write_only': True}  # Accept uploads but don't return raw field
        }
    
    def get_image_url(self, obj):
        """Return the full Cloudinary URL for the image"""
        if obj.image:
            return obj.image.url
        return None
    
    def create(self, validated_data):
        """Handle image upload when creating menu item"""
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Handle image upload when updating menu item"""
        return super().update(instance, validated_data)
    

class OrderSerializer(serializers.ModelSerializer):
    items = MenuItemSerializer(many=True, read_only=True)
    items_ids = serializers.PrimaryKeyRelatedField(queryset=MenuItem.objects.all(), many=True, write_only=True, source='items')
    user_name = serializers.CharField(source='user.name', read_only=True, default='Unknown')
    delivery_charge = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = ['id', 'user', 'user_name', 'items', 'items_ids', 'status', 'total_price', 
                  'created_at', 'phone', 'location', 'latitude', 'longitude', 'delivery_charge', 'items_data']
        # IMPORTANT: latitude and longitude should NOT be in read_only_fields
        read_only_fields = ['user', 'status', 'total_price', 'created_at']  # Don't include latitude/longitude here!
    
    def get_delivery_charge(self, obj):
        return 50.00
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Add quantities and prices from items_data
        items_data = instance.items_data
        if items_data:
            data['items'] = [
                {**item, 'quantity': next((i['quantity'] for i in items_data if i['id'] == item['id']), 1),
                 'price': next((i['price'] for i in items_data if i['id'] == item['id']), item['price'])}
                for item in data['items']
            ]
        return data
        
class AdminOrderSerializer(serializers.ModelSerializer):  # New serializer for admin updates
    items = MenuItemSerializer(many=True, read_only=True)
    items_ids = serializers.PrimaryKeyRelatedField(queryset=MenuItem.objects.all(), many=True, write_only=True, source='items')

    class Meta:
        model = Order
        fields = ['id', 'user', 'items', 'items_ids', 'status', 'total_price', 'created_at', 'phone', 'location','latitude','longitude']
        read_only_fields = ['user', 'total_price', 'created_at']  # Status is writable for admins



#delivery status serializer 
class DeliveryStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryStatus
        fields = ['available', 'updated_at']