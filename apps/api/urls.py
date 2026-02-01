"""
API URL Configuration
All REST API endpoints for the BikeShop e-commerce platform
"""
from django.urls import path

from api.views import (
    # Auth views
    RegisterView,
    LoginView,
    ProfileView,
    ChangePasswordView,
    AddressListCreateView,
    AddressDetailView,
    ForgotPasswordView,
    VerifyResetTokenView,
    ResetPasswordView,
    
    # Catalog views
    ProductListView,
    ProductDetailView,
    CategoryListView,
    CategoryDetailView,
    BrandListView,
    BrandDetailView,
    ProductSearchView,
    
    # Homepage views
    HomepageView,
    
    # Cart views
    CartView,
    AddToCartView,
    UpdateCartItemView,
    RemoveCartItemView,
    ClearCartView,
    
    # Order views
    OrderListView,
    OrderDetailView,
    CreateOrderView,
    CancelOrderView,
)

app_name = 'api'

# API URL patterns
urlpatterns = [
    # ============================================================================
    # AUTHENTICATION & USER MANAGEMENT ENDPOINTS
    # ============================================================================
    
    # Auth endpoints
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/profile/', ProfileView.as_view(), name='profile'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='change-password'),
    
    # Password reset endpoints
    path('auth/forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('auth/verify-reset-token/', VerifyResetTokenView.as_view(), name='verify-reset-token'),
    path('auth/reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    
    # Address management
    path('auth/addresses/', AddressListCreateView.as_view(), name='address-list-create'),
    path('auth/addresses/<int:pk>/', AddressDetailView.as_view(), name='address-detail'),
    
    # ============================================================================
    # CATALOG ENDPOINTS
    # ============================================================================
    
    # Products
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/<slug:slug>/', ProductDetailView.as_view(), name='product-detail'),
    
    # Categories
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/<slug:slug>/', CategoryDetailView.as_view(), name='category-detail'),
    
    # Brands
    path('brands/', BrandListView.as_view(), name='brand-list'),
    path('brands/<slug:slug>/', BrandDetailView.as_view(), name='brand-detail'),
    
    # Search
    path('search/', ProductSearchView.as_view(), name='product-search'),
    
    # ============================================================================
    # HOMEPAGE CONTENT
    # ============================================================================
    
    path('homepage/', HomepageView.as_view(), name='homepage'),
    
    # ============================================================================
    # CART ENDPOINTS
    # ============================================================================
    
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/items/', AddToCartView.as_view(), name='cart-add'),
    path('cart/items/<int:pk>/', UpdateCartItemView.as_view(), name='cart-item-detail'),
    path('cart/clear/', ClearCartView.as_view(), name='cart-clear'),
    
    # ============================================================================
    # ORDER ENDPOINTS
    # ============================================================================
    
    path('orders/', OrderListView.as_view(), name='order-list'),
    path('orders/create/', CreateOrderView.as_view(), name='order-create'),
    path('orders/<str:order_number>/', OrderDetailView.as_view(), name='order-detail'),
    path('orders/<str:order_number>/cancel/', CancelOrderView.as_view(), name='order-cancel'),
]
