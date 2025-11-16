"""
Cart API Serializers
"""
from rest_framework import serializers
from decimal import Decimal

from cart.models import Cart, CartItem
from catalog.models import ProductVariant
from api.serializers.catalog import ProductListSerializer


class CartItemVariantSerializer(serializers.ModelSerializer):
    """Serializer for variant details in cart item"""
    product = ProductListSerializer(read_only=True)
    attributes = serializers.SerializerMethodField()
    sale_price = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductVariant
        fields = ['id', 'sku', 'product', 'price', 'sale_price', 'attributes']
    
    def get_attributes(self, obj):
        """Get variant attributes as list of dicts"""
        return [
            {
                'type': attr.attribute_value.attribute_type.name,
                'value': attr.attribute_value.value
            }
            for attr in obj.attributes.select_related(
                'attribute_value__attribute_type'
            ).all()
        ]
    
    def get_sale_price(self, obj):
        """Return sale price if on sale, else None"""
        if obj.is_on_sale():
            return str(obj.sale_price)
        return None


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for cart items - supports both variants and base products"""
    variant = CartItemVariantSerializer(read_only=True)
    product = ProductListSerializer(read_only=True)
    total = serializers.SerializerMethodField()
    savings = serializers.SerializerMethodField()
    is_available = serializers.SerializerMethodField()
    item_type = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = [
            'id', 'variant', 'product', 'item_type', 'quantity', 'price_snapshot',
            'total', 'savings', 'is_available'
        ]
    
    def get_item_type(self, obj):
        """Return 'variant' or 'product' to identify item type"""
        if obj.variant:
            return 'variant'
        elif obj.product:
            return 'product'
        return 'unknown'
    
    def get_total(self, obj):
        """Calculate total for this item"""
        return str(obj.get_total())
    
    def get_savings(self, obj):
        """Calculate savings for this item"""
        savings = obj.get_savings()
        return str(savings) if savings > 0 else "0.00"
    
    def get_is_available(self, obj):
        """Check if item is still available"""
        return obj.is_available()


class CartSerializer(serializers.ModelSerializer):
    """Serializer for cart with items"""
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.SerializerMethodField()
    subtotal = serializers.SerializerMethodField()
    total_savings = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_items', 'subtotal', 'total_savings']
    
    def get_total_items(self, obj):
        """Get total number of items"""
        return obj.get_total_items()
    
    def get_subtotal(self, obj):
        """Get cart subtotal"""
        return str(obj.get_subtotal())
    
    def get_total_savings(self, obj):
        """Get total savings"""
        return str(obj.get_total_savings())


class AddToCartSerializer(serializers.Serializer):
    """Serializer for adding items to cart - supports both variants and base products"""
    variant_id = serializers.IntegerField(required=False, allow_null=True)
    product_id = serializers.IntegerField(required=False, allow_null=True)
    quantity = serializers.IntegerField(required=True, min_value=1)
    
    def validate(self, data):
        """Validate that either variant_id or product_id is provided (not both)"""
        variant_id = data.get('variant_id')
        product_id = data.get('product_id')
        
        # Must provide either variant_id or product_id
        if not variant_id and not product_id:
            raise serializers.ValidationError({
                'error': 'Either variant_id or product_id must be provided'
            })
        
        # Cannot provide both
        if variant_id and product_id:
            raise serializers.ValidationError({
                'error': 'Cannot provide both variant_id and product_id'
            })
        
        # Validate variant if provided
        if variant_id:
            try:
                from catalog.models import ProductVariant
                variant = ProductVariant.objects.get(id=variant_id)
                if not variant.is_active:
                    raise serializers.ValidationError({
                        'variant_id': 'This product variant is not available'
                    })
                # Check stock
                if data['quantity'] > variant.stock:
                    raise serializers.ValidationError({
                        'stock': f"Only {variant.stock} items available in stock"
                    })
            except ProductVariant.DoesNotExist:
                raise serializers.ValidationError({
                    'variant_id': 'Variant not found'
                })
        
        # Validate product if provided
        if product_id:
            try:
                from catalog.models import Product
                product = Product.objects.get(id=product_id)
                if not product.is_active:
                    raise serializers.ValidationError({
                        'product_id': 'This product is not available'
                    })
                # Check if product has variants (should use variant_id instead)
                if product.variants.filter(is_active=True).exists():
                    raise serializers.ValidationError({
                        'product_id': 'This product has variants. Please use variant_id instead'
                    })
                # Check stock
                if data['quantity'] > product.stock:
                    raise serializers.ValidationError({
                        'stock': f"Only {product.stock} items available in stock"
                    })
            except Product.DoesNotExist:
                raise serializers.ValidationError({
                    'product_id': 'Product not found'
                })
        
        return data
    
    def validate_quantity(self, value):
        """Validate quantity is positive"""
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1")
        return value


class UpdateCartItemSerializer(serializers.Serializer):
    """Serializer for updating cart item quantity"""
    quantity = serializers.IntegerField(required=True, min_value=1)
    
    def validate_quantity(self, value):
        """Validate quantity is positive"""
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1")
        return value
