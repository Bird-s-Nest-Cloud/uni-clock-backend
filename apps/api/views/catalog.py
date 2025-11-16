"""
API Views for catalog (products, categories, brands)
"""
from rest_framework import generics, filters
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Min, Max, F

from catalog.models import Product, Category, Brand
from api.serializers import (
    ProductListSerializer,
    ProductDetailSerializer,
    CategorySerializer,
    CategoryDetailSerializer,
    BrandSerializer,
    BrandDetailSerializer,
)
from api.utils import StandardResponseMixin


class ProductListView(StandardResponseMixin, generics.ListAPIView):
    """
    GET /api/products/
    List all products with filtering, searching, and pagination
    """
    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_at', 'title']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Get filtered queryset"""
        queryset = Product.objects.filter(is_active=True).select_related(
            'category', 'brand'
        ).prefetch_related('images', 'variants')
        
        # Category filter - support multiple categories (comma-separated)
        category_param = self.request.query_params.get('category')
        if category_param:
            category_slugs = [slug.strip() for slug in category_param.split(',') if slug.strip()]
            if category_slugs:
                queryset = queryset.filter(category__slug__in=category_slugs)
        
        # Brand filter - support multiple brands (comma-separated)
        brand_param = self.request.query_params.get('brand')
        if brand_param:
            brand_slugs = [slug.strip() for slug in brand_param.split(',') if slug.strip()]
            if brand_slugs:
                queryset = queryset.filter(brand__slug__in=brand_slugs)
        
        # Price range filter
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        
        if min_price:
            queryset = queryset.filter(
                Q(price__gte=min_price) | Q(variants__price__gte=min_price)
            )
        
        if max_price:
            queryset = queryset.filter(
                Q(price__lte=max_price) | Q(variants__price__lte=max_price)
            )
        
        # Featured filter
        is_featured = self.request.query_params.get('is_featured')
        if is_featured and is_featured.lower() == 'true':
            queryset = queryset.filter(is_featured=True)
        
        # On sale filter
        on_sale = self.request.query_params.get('on_sale')
        if on_sale and on_sale.lower() == 'true':
            queryset = queryset.filter(
                Q(sale_price__isnull=False, sale_price__lt=F('price')) |
                Q(variants__sale_price__isnull=False)
            )
        
        return queryset.distinct()


class ProductDetailView(StandardResponseMixin, generics.RetrieveAPIView):
    """
    GET /api/products/{slug}/
    Get product detail by slug
    """
    serializer_class = ProductDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'
    
    def get_queryset(self):
        """Get active products with related data"""
        return Product.objects.filter(is_active=True).select_related(
            'category', 'brand'
        ).prefetch_related('images', 'variants', 'variants__attributes', 'variants__attributes__attribute_value', 'variants__attributes__attribute_value__attribute_type')


class CategoryListView(StandardResponseMixin, generics.ListAPIView):
    """
    GET /api/categories/
    List all active categories 
    """
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    queryset = Category.objects.filter(is_active=True).prefetch_related('products')
    pagination_class = None  # No pagination for categories


class CategoryDetailView(StandardResponseMixin, generics.RetrieveAPIView):
    """
    GET /api/categories/{slug}/
    Get category detail with products
    """
    serializer_class = CategoryDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'
    
    def get_queryset(self):
        """Get active categories with active products"""
        return Category.objects.filter(is_active=True).prefetch_related(
            'products__images',
            'products__brand',
            'products__variants'
        )


class BrandListView(StandardResponseMixin, generics.ListAPIView):
    """
    GET /api/brands/
    List all active brands
    """
    serializer_class = BrandSerializer
    permission_classes = [AllowAny]
    queryset = Brand.objects.filter(is_active=True).prefetch_related('products')
    pagination_class = None  # No pagination for brands


class BrandDetailView(StandardResponseMixin, generics.RetrieveAPIView):
    """
    GET /api/brands/{slug}/
    Get brand detail with products
    """
    serializer_class = BrandDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'
    
    def get_queryset(self):
        """Get active brands with active products"""
        return Brand.objects.filter(is_active=True).prefetch_related(
            'products__images',
            'products__category',
            'products__variants'
        )
