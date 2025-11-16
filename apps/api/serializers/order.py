"""
Serializers for Order API
"""
from rest_framework import serializers
from orders.models import Order, OrderItem, Payment
from accounts.models import Address
from api.serializers.catalog import ProductListSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for order items"""
    product = ProductListSerializer(read_only=True)
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'variant', 'product_title', 'variant_sku',
            'variant_attributes', 'quantity', 'unit_price', 'subtotal'
        ]


class OrderAddressSerializer(serializers.ModelSerializer):
    """Serializer for order addresses"""
    class Meta:
        model = Address
        fields = [
            'id', 'label', 'street', 'city', 'state', 'postal_code', 'country', 'phone'
        ]


class OrderListSerializer(serializers.ModelSerializer):
    """Serializer for order list view"""
    total_items = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'payment_status',
            'total_items', 'total_price', 'created_at'
        ]
    
    def get_total_items(self, obj):
        return obj.get_total_items()


class OrderDetailSerializer(serializers.ModelSerializer):
    """Serializer for order detail view"""
    items = OrderItemSerializer(many=True, read_only=True)
    billing_address = serializers.SerializerMethodField()
    shipping_address = serializers.SerializerMethodField()
    total_items = serializers.SerializerMethodField()
    payment_method = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'payment_status',
            'billing_address', 'shipping_address', 'guest_email', 'guest_phone', 'items',
            'subtotal', 'discount', 'shipping_cost', 'total_price',
            'total_items', 'payment_method', 'notes', 'created_at', 'updated_at'
        ]
    
    def get_billing_address(self, obj):
        """Return billing address from ForeignKey or guest data"""
        if obj.billing_address:
            return OrderAddressSerializer(obj.billing_address).data
        elif obj.guest_billing_address_data:
            return obj.guest_billing_address_data
        return None
    
    def get_shipping_address(self, obj):
        """Return shipping address from ForeignKey or guest data"""
        if obj.shipping_address:
            return OrderAddressSerializer(obj.shipping_address).data
        elif obj.guest_shipping_address_data:
            return obj.guest_shipping_address_data
        return None
    
    def get_total_items(self, obj):
        return obj.get_total_items()
    
    def get_payment_method(self, obj):
        if hasattr(obj, 'payment'):
            return obj.payment.get_method_display()
        return None


class GuestAddressSerializer(serializers.Serializer):
    """Serializer for guest user addresses during checkout"""
    label = serializers.CharField(max_length=50, default='Guest Address')
    phone = serializers.CharField(max_length=20)
    street = serializers.CharField(max_length=255)
    city = serializers.CharField(max_length=100)
    state = serializers.CharField(max_length=100)
    postal_code = serializers.CharField(max_length=20)
    country = serializers.CharField(max_length=100, default='Bangladesh')


class CreateOrderSerializer(serializers.Serializer):
    """Serializer for creating an order from cart"""
    billing_address_id = serializers.IntegerField(required=False, allow_null=True)
    shipping_address_id = serializers.IntegerField(required=False, allow_null=True)
    
    # Guest user fields
    guest_email = serializers.EmailField(required=False, allow_null=True)
    guest_phone = serializers.CharField(max_length=20, required=False, allow_null=True)
    guest_billing_address = GuestAddressSerializer(required=False, allow_null=True)
    guest_shipping_address = GuestAddressSerializer(required=False, allow_null=True)
    
    # Optional fields
    discount = serializers.DecimalField(max_digits=10, decimal_places=2, default=0, required=False)
    shipping_cost = serializers.DecimalField(max_digits=10, decimal_places=2, default=0, required=False)
    notes = serializers.CharField(max_length=500, required=False, allow_blank=True)
    
    # Payment info
    payment_method = serializers.ChoiceField(
        choices=['cod', 'card', 'bkash', 'nagad'],
        default='cod'
    )
    
    def validate(self, data):
        """Validate that addresses are provided"""
        request = self.context.get('request')
        
        # For authenticated users
        if request and request.user.is_authenticated:
            # Can use address IDs or guest addresses
            if not data.get('billing_address_id') and not data.get('guest_billing_address'):
                raise serializers.ValidationError({
                    'billing_address': 'Billing address is required'
                })
            if not data.get('shipping_address_id') and not data.get('guest_shipping_address'):
                raise serializers.ValidationError({
                    'shipping_address': 'Shipping address is required'
                })
        else:
            # For guest users, address details are required
            if not data.get('guest_billing_address'):
                raise serializers.ValidationError({
                    'guest_billing_address': 'Billing address details are required for guest checkout'
                })
            if not data.get('guest_shipping_address'):
                raise serializers.ValidationError({
                    'guest_shipping_address': 'Shipping address details are required for guest checkout'
                })
        
        return data
