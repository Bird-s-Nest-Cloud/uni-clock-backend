"""
API Views
Export all API views from modules
"""

# Auth views
from .auth import (
    RegisterView,
    LoginView,
    ProfileView,
    ChangePasswordView,
    AddressListCreateView,
    AddressDetailView,
    ForgotPasswordView,
    VerifyResetTokenView,
    ResetPasswordView,
)

# Catalog views
from .catalog import (
    ProductListView,
    ProductDetailView,
    CategoryListView,
    CategoryDetailView,
    BrandListView,
    BrandDetailView,
    ProductSearchView,
)

# Homepage views
from .homepage import HomepageView

# Cart views
from .cart import (
    CartView,
    AddToCartView,
    UpdateCartItemView,
    RemoveCartItemView,
    ClearCartView,
)

# Order views
from .order import (
    OrderListView,
    OrderDetailView,
    CreateOrderView,
    CancelOrderView,
)

__all__ = [
    # Auth
    'RegisterView',
    'LoginView',
    'ProfileView',
    'ChangePasswordView',
    'AddressListCreateView',
    'AddressDetailView',
    'ForgotPasswordView',
    'VerifyResetTokenView',
    'ResetPasswordView',
    
    # Catalog
    'ProductListView',
    'ProductDetailView',
    'CategoryListView',
    'CategoryDetailView',
    'BrandListView',
    'BrandDetailView',
    'ProductSearchView',
    
    # Homepage
    'HomepageView',
    
    # Cart
    'CartView',
    'AddToCartView',
    'UpdateCartItemView',
    'RemoveCartItemView',
    'ClearCartView',
    
    # Order
    'OrderListView',
    'OrderDetailView',
    'CreateOrderView',
    'CancelOrderView',
]
