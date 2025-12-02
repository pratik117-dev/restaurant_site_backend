import csv
from django.http import HttpResponse
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .models import MenuItem, Order, CustomUser, OTP
from .serializers import UserSerializer, LoginSerializer, MenuItemSerializer, OrderSerializer, AdminOrderSerializer  # Added AdminOrderSerializer




from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import random
from django.contrib.auth.hashers import make_password

class RegisterView(generics.GenericAPIView):
    serializer_class = UserSerializer

    def post(self, request):
        email = request.data.get('email')
        name = request.data.get('name')
        password = request.data.get('password')

        if CustomUser.objects.filter(email=email).exists():
            return Response({'error': 'Email already registered'}, status=status.HTTP_400_BAD_REQUEST)

        # Generate OTP
        otp = str(random.randint(100000, 999999))

        # Send OTP email
        send_mail(
            'Your OTP for Registration',
            f'Your OTP is {otp}. It expires in 10 minutes.',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

        # Store in database
        OTP.objects.filter(email=email).delete()
        OTP.objects.create(email=email, otp=otp, name=name, password=make_password(password))

        return Response({'message': 'OTP sent to your email'}, status=status.HTTP_200_OK)

class VerifyOTPView(generics.GenericAPIView):
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')

        try:
            otp_obj = OTP.objects.get(email=email, otp=otp)
            if otp_obj.is_expired():
                return Response({'error': 'OTP expired'}, status=status.HTTP_400_BAD_REQUEST)
        except OTP.DoesNotExist:
            return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

        # Create user with hashed password
        user = CustomUser(
            email=otp_obj.email,
            name=otp_obj.name,
            password=otp_obj.password  # Already hashed
        )
        user.save()  # Save without hashing again

        # Delete OTP
        otp_obj.delete()

        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': {'email': user.email, 'name': user.name, 'is_admin': user.is_admin}}, status=status.HTTP_201_CREATED)


# Rest of the views remain the same
class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, email=email, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'user': {'email': user.email, 'name': user.name, 'is_admin': user.is_admin}})
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

class MenuListView(generics.ListAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer



class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        items_data = self.request.data.get('items_data', [])
        total_price = self.request.data.get('total_price')
        if total_price:
            total_price = Decimal(total_price)
        else:
            subtotal = sum(item['price'] * item['quantity'] for item in items_data)
            delivery_charge = Decimal('50.00')
            total_price = subtotal + delivery_charge
        serializer.save(user=self.request.user, total_price=total_price, items_data=items_data)


class AdminOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return Order.objects.exclude(status='CANCELLED')

class AdminOrderUpdateView(generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = AdminOrderSerializer  # Use the new serializer that allows status updates
    permission_classes = [IsAdminUser]
    http_method_names = ['patch']

class AdminOrderDeleteView(generics.DestroyAPIView):
    queryset = Order.objects.all()
    permission_classes = [IsAdminUser]

class CheckoutUpdateView(generics.UpdateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['patch']

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

class CurrentUserView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
    

class DownloadOrdersView(generics.GenericAPIView):  # New view for downloading orders as CSV
    permission_classes = [IsAdminUser]
    def get(self, request):
        orders = Order.objects.all()  # Get all orders (or filter as needed)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="orders.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Order ID', 'User Email','User Name', 'Items', 'Status', 'Total Price', 'Phone', 'Location', 'Created At'])
        
        for order in orders:
            items = ', '.join([item.name for item in order.items.all()])
            writer.writerow([
                order.id,
                order.user.email,
                order.user.name,
                items,
                order.status,
                order.total_price,
                order.phone or 'Not provided',
                order.location or 'Not provided',
                order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            ])
        
        return response
    

class AdminMenuDeleteView(generics.DestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAdminUser]


class AdminMenuListView(generics.ListCreateAPIView):  # Handles adding (POST) and listing (GET) menu items
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAdminUser]


class AdminMenuUpdateView(generics.UpdateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAdminUser]
    http_method_names = ['put']
    partial = True  # Allow partial updates