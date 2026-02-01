"""
API Serializers for catalog (products, categories, brands)
"""
from rest_framework import serializers
from catalog.models import Product, ProductVariant, ProductImage, Category, Brand, VariantAttribute


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model"""
    product_count = serializers.SerializerMethodField()
    parent_id = serializers.IntegerField(source='parent.id', read_only=True, allow_null=True)
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image', 'parent_id', 'product_count']
    
    def get_product_count(self, obj):
        """Get active product count for category"""
        request = self.context.get('request')
        watch_pref = request.headers.get('X-Watch-Pref', 'authentic') if request else 'authentic'
        # Check if preference is explicitly 'replica', otherwise treat as authentic
        is_authentic = watch_pref != 'replica'
        return obj.products.filter(is_active=True, authentic=is_authentic).count()


class BrandSerializer(serializers.ModelSerializer):
    """Serializer for Brand model"""
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Brand
        fields = ['id', 'name', 'slug', 'description', 'logo', 'website', 'product_count']
    
    def get_product_count(self, obj):
        """Get active product count for brand"""
        request = self.context.get('request')
        watch_pref = request.headers.get('X-Watch-Pref', 'authentic') if request else 'authentic'
        # Check if preference is explicitly 'replica', otherwise treat as authentic
        is_authentic = watch_pref != 'replica'
        return obj.products.filter(is_active=True, authentic=is_authentic).count()


class ProductSearchSerializer(serializers.ModelSerializer):
    """Serializer for Product Search Results"""
    image = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ['title', 'slug', 'image']
    
    def get_image(self, obj):
        """Get primary product image (first by position)"""
        primary_image = obj.images.order_by('position').first()
        if primary_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(primary_image.image.url)
            return primary_image.image.url
        return None


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for Product Images"""
    
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'position']


class VariantAttributeSerializer(serializers.ModelSerializer):
    """Serializer for Variant Attributes"""
    type = serializers.CharField(source='attribute_value.attribute_type.name')
    value = serializers.CharField(source='attribute_value.value')
    
    class Meta:
        model = VariantAttribute
        fields = ['type', 'value']


class ProductVariantSerializer(serializers.ModelSerializer):
    """Serializer for Product Variant"""
    attributes = VariantAttributeSerializer(many=True, read_only=True)
    is_on_sale = serializers.SerializerMethodField()
    discount_percentage = serializers.SerializerMethodField()
    is_in_stock = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductVariant
        fields = [
            'id', 'sku', 'price', 'sale_price', 'stock',
            'is_on_sale', 'discount_percentage', 'is_in_stock', 'attributes'
        ]
    
    def get_is_on_sale(self, obj):
        """Check if variant is on sale"""
        return obj.sale_price is not None and obj.sale_price < obj.price
    
    def get_discount_percentage(self, obj):
        """Calculate discount percentage"""
        if obj.sale_price and obj.sale_price < obj.price:
            discount = ((obj.price - obj.sale_price) / obj.price) * 100
            return round(discount, 0)
        return None
    
    def get_is_in_stock(self, obj):
        """Check if variant is in stock"""
        return obj.stock > 0


class ProductListSerializer(serializers.ModelSerializer):
    """Serializer for Product List"""
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    primary_image = serializers.SerializerMethodField()
    min_price = serializers.SerializerMethodField()
    max_price = serializers.SerializerMethodField()
    is_on_sale = serializers.SerializerMethodField()
    discount_percentage = serializers.SerializerMethodField()
    variant_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'category', 'brand', 'price', 'sale_price',
            'min_price', 'max_price', 'is_on_sale', 'discount_percentage',
            'stock', 'primary_image', 'variant_count', 'authentic'
        ]
    
    def get_primary_image(self, obj):
        """Get primary product image URL"""
        request = self.context.get('request')
        image = obj.images.filter(position=0).first()
        if image and image.image:
            return request.build_absolute_uri(image.image.url) if request else image.image.url
        return None
    
    def get_min_price(self, obj):
        """Get minimum price from variants"""
        variants = obj.variants.all()
        if variants:
            prices = [v.sale_price if v.sale_price else v.price for v in variants]
            return min(prices) if prices else obj.price
        return obj.price
    
    def get_max_price(self, obj):
        """Get maximum price from variants"""
        variants = obj.variants.all()
        if variants:
            prices = [v.price for v in variants]
            return max(prices) if prices else obj.price
        return obj.price
    
    def get_is_on_sale(self, obj):
        """Check if product or any variant is on sale"""
        if obj.sale_price and obj.sale_price < obj.price:
            return True
        return obj.variants.filter(sale_price__isnull=False).exists()
    
    def get_discount_percentage(self, obj):
        """Calculate maximum discount percentage"""
        discounts = []
        
        # Product level discount
        if obj.sale_price and obj.sale_price < obj.price:
            discount = ((obj.price - obj.sale_price) / obj.price) * 100
            discounts.append(discount)
        
        # Variant discounts
        for variant in obj.variants.all():
            if variant.sale_price and variant.sale_price < variant.price:
                discount = ((variant.price - variant.sale_price) / variant.price) * 100
                discounts.append(discount)
        
        return round(max(discounts), 0) if discounts else None
    
    def get_variant_count(self, obj):
        """Get count of variants"""
        return obj.variants.count()


class ProductDetailSerializer(ProductListSerializer):
    """Serializer for Product Detail"""
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    available_attributes = serializers.SerializerMethodField()
    
    class Meta(ProductListSerializer.Meta):
        fields = ProductListSerializer.Meta.fields + ['description', 'weight', 'images', 'variants', 'available_attributes']
    
    def get_available_attributes(self, obj):
        """Get all available attribute types and values from all variants"""
        from collections import defaultdict
        
        attributes_map = defaultdict(set)
        
        # Collect all unique attribute values per type from all variants
        for variant in obj.variants.filter(is_active=True):
            for variant_attr in variant.attributes.select_related('attribute_value__attribute_type'):
                attr_type = variant_attr.attribute_value.attribute_type.name
                attr_value = variant_attr.attribute_value.value
                attributes_map[attr_type].add(attr_value)
        
        # Convert to list format
        result = []
        for attr_type, values in attributes_map.items():
            result.append({
                'type': attr_type,
                'values': sorted(list(values))
            })
        
        # Sort by attribute type name for consistency
        return sorted(result, key=lambda x: x['type'])


class CategoryDetailSerializer(CategorySerializer):
    """Serializer for Category Detail with products"""
    products = serializers.SerializerMethodField()
    
    class Meta(CategorySerializer.Meta):
        fields = CategorySerializer.Meta.fields + ['products']
    
    def get_products(self, obj):
        """Get products filtered by watch preference"""
        request = self.context.get('request')
        watch_pref = request.headers.get('X-Watch-Pref', 'authentic') if request else 'authentic'
        # Check if preference is explicitly 'replica', otherwise treat as authentic
        is_authentic = watch_pref != 'replica'
        
        products = obj.products.filter(is_active=True, authentic=is_authentic)
        return ProductListSerializer(products, many=True, context=self.context).data


class BrandDetailSerializer(BrandSerializer):
    """Serializer for Brand Detail with products"""
    products = serializers.SerializerMethodField()
    
    class Meta(BrandSerializer.Meta):
        fields = BrandSerializer.Meta.fields + ['products']
    
    def get_products(self, obj):
        """Get products filtered by watch preference"""
        request = self.context.get('request')
        watch_pref = request.headers.get('X-Watch-Pref', 'authentic') if request else 'authentic'
        # Check if preference is explicitly 'replica', otherwise treat as authentic
        is_authentic = watch_pref != 'replica'
        
        products = obj.products.filter(is_active=True, authentic=is_authentic)
        return ProductListSerializer(products, many=True, context=self.context).data
