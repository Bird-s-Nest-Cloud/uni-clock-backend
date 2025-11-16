"""
API Serializers for homepage content (banners and featured sections)
"""
from rest_framework import serializers
from core.models import Banner, FeaturedSection
from catalog.models import Category, Brand
from .catalog import ProductListSerializer


class HomepageProductSerializer(serializers.ModelSerializer):
    """Simplified product serializer for homepage"""
    primary_image = serializers.SerializerMethodField()
    is_on_sale = serializers.SerializerMethodField()
    
    class Meta:
        from catalog.models import Product
        model = Product
        fields = ['id', 'title', 'slug', 'price', 'sale_price', 'primary_image', 'is_on_sale']
    
    def get_primary_image(self, obj):
        """Get primary product image URL"""
        request = self.context.get('request')
        image = obj.images.filter(position=0).first()
        if image and image.image:
            return request.build_absolute_uri(image.image.url) if request else image.image.url
        return None
    
    def get_is_on_sale(self, obj):
        """Check if product is on sale"""
        return obj.sale_price is not None and obj.sale_price < obj.price


class HomepageCategorySerializer(serializers.ModelSerializer):
    """Simplified category serializer for homepage"""
    image_url = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image_url', 'product_count']
    
    def get_image_url(self, obj):
        """Get category image URL"""
        if obj.image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None
    
    def get_product_count(self, obj):
        """Get active product count for category"""
        return obj.products.filter(is_active=True).count()


class HomepageBrandSerializer(serializers.ModelSerializer):
    """Simplified brand serializer for homepage"""
    logo_url = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Brand
        fields = ['id', 'name', 'slug', 'description', 'logo_url', 'website', 'product_count']
    
    def get_logo_url(self, obj):
        """Get brand logo URL"""
        if obj.logo:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.logo.url) if request else obj.logo.url
        return None
    
    def get_product_count(self, obj):
        """Get active product count for brand"""
        return obj.products.filter(is_active=True).count()


class BannerLinkProductSerializer(serializers.Serializer):
    """Serializer for banner linked product"""
    id = serializers.IntegerField()
    title = serializers.CharField()
    slug = serializers.CharField()


class BannerSerializer(serializers.ModelSerializer):
    """Serializer for Homepage Banners"""
    image_mobile = serializers.ImageField(source='mobile_image', read_only=True)
    link_product = BannerLinkProductSerializer(read_only=True)
    
    class Meta:
        model = Banner
        fields = [
            'id', 'title', 'subtitle', 'image', 'image_mobile',
            'link_product', 'button_text', 'display_order'
        ]


class FeaturedSectionSerializer(serializers.ModelSerializer):
    """Serializer for Featured Sections with products"""
    products = serializers.SerializerMethodField()
    
    class Meta:
        model = FeaturedSection
        fields = ['id', 'title', 'subtitle', 'section_type', 'products']
    
    def get_products(self, obj):
        """Get products based on section type"""
        products = obj.get_products()
        return HomepageProductSerializer(
            products,
            many=True,
            context=self.context
        ).data
