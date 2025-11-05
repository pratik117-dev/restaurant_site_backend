from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.urlpatterns import format_suffix_patterns


urlpatterns = [
    path('auth/register/', views.RegisterView.as_view()),
    path('auth/verify-otp/', views.VerifyOTPView.as_view()),
    path('auth/login/', views.LoginView.as_view()),
    path('auth/me/', views.CurrentUserView.as_view()),
    path('menu/', views.MenuListView.as_view()),
    path('orders/', views.OrderListCreateView.as_view()),
    path('orders/<int:pk>/checkout/', views.CheckoutUpdateView.as_view()),
    path('admin/orders/', views.AdminOrderListView.as_view()),
    path('admin/orders/<int:pk>/', views.AdminOrderUpdateView.as_view()),
    path('admin/orders/<int:pk>/delete/', views.AdminOrderDeleteView.as_view()),
    path('admin/orders/download/', views.DownloadOrdersView.as_view()),
    path('admin/menu/', views.AdminMenuListView.as_view()),  # Added: For adding menu items (POST)
    path('admin/menu/<int:pk>/delete/', views.AdminMenuDeleteView.as_view()), #for deleting the item 
    path('admin/menu/<int:pk>/', views.AdminMenuUpdateView.as_view()),  # Add this for PUT updates
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
   


urlpatterns = format_suffix_patterns(urlpatterns)