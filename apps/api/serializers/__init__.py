"""
API Serializers package
"""
from .auth import (
    UserSerializer,
    UserProfileSerializer,
    RegisterSerializer,
    LoginSerializer,
    ChangePasswordSerializer,
    AddressSerializer,
    ForgotPasswordSerializer,
    VerifyResetTokenSerializer,
    ResetPasswordSerializer,
    generate_jwt_token
)

from .catalog import (
    CategorySerializer,
    CategoryDetailSerializer,
    BrandSerializer,
    BrandDetailSerializer,
    ProductListSerializer,
    ProductDetailSerializer,
    ProductVariantSerializer,
    ProductSearchSerializer,
)

from .homepage import (
    BannerSerializer,
    FeaturedSectionSerializer,
    HomepageCategorySerializer,
    HomepageBrandSerializer,
)

from .cart import (
    CartSerializer,
    CartItemSerializer,
    AddToCartSerializer,
    UpdateCartItemSerializer,
)

from .order import (
    OrderListSerializer,
    OrderDetailSerializer,
    OrderItemSerializer,
    CreateOrderSerializer,
)

__all__ = [
    # Auth
    'UserSerializer',
    'UserProfileSerializer',
    'RegisterSerializer',
    'LoginSerializer',
    'ChangePasswordSerializer',
    'AddressSerializer',
    'ForgotPasswordSerializer',
    'VerifyResetTokenSerializer',
    'ResetPasswordSerializer',
    'generate_jwt_token',
    # Catalog
    'CategorySerializer',
    'CategoryDetailSerializer',
    'BrandSerializer',
    'BrandDetailSerializer',
    'ProductListSerializer',
    'ProductDetailSerializer',
    'ProductVariantSerializer',
    # Homepage
    'BannerSerializer',
    'FeaturedSectionSerializer',
    'HomepageCategorySerializer',
    'HomepageBrandSerializer',
    # Cart
    'CartSerializer',
    'CartItemSerializer',
    'AddToCartSerializer',
    'UpdateCartItemSerializer',
    # Order
    'OrderListSerializer',
    'OrderDetailSerializer',
    'OrderItemSerializer',
    'CreateOrderSerializer',
]
