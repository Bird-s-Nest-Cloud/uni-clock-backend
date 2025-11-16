"""
API Views for Order management
"""
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db import transaction

from orders.models import Order, OrderItem, Payment
from accounts.models import Address
from cart.models import Cart
from api.serializers import (
    OrderListSerializer,
    OrderDetailSerializer,
    CreateOrderSerializer,
)
from api.utils import success_response, error_response, created_response, not_found_response, bad_request_response
from api.pagination import LaravelStylePagination


class OrderListView(APIView):
    """
    GET /api/orders/ - List all orders for authenticated user or guest
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get orders for authenticated user or guest"""
        if request.user.is_authenticated:
            orders = Order.objects.filter(user=request.user).prefetch_related('items')
        else:
            # Get orders for guest user by session
            if not request.session.session_key:
                return success_response(
                    data={'results': [], 'pagination': {}},
                    message="No orders found"
                )
            
            session_key = request.session.session_key
            orders = Order.objects.filter(
                session_key=session_key,
                user__isnull=True
            ).prefetch_related('items')
        
        # Paginate results
        paginator = LaravelStylePagination()
        paginated_orders = paginator.paginate_queryset(orders, request)
        
        serializer = OrderListSerializer(paginated_orders, many=True)
        
        # get_paginated_response already returns the standardized response format
        return paginator.get_paginated_response(serializer.data)


class OrderDetailView(APIView):
    """
    GET /api/orders/{order_number}/ - Get order details
    """
    permission_classes = [AllowAny]
    
    def get(self, request, order_number):
        """Get order details"""
        try:
            if request.user.is_authenticated:
                order = Order.objects.prefetch_related(
                    'items__product__images',
                    'items__variant'
                ).select_related(
                    'billing_address',
                    'shipping_address'
                ).get(
                    order_number=order_number,
                    user=request.user
                )
            else:
                # Guest user - check session
                if not request.session.session_key:
                    return not_found_response(message="Order not found")
                
                order = Order.objects.prefetch_related(
                    'items__product__images',
                    'items__variant'
                ).select_related(
                    'billing_address',
                    'shipping_address'
                ).get(
                    order_number=order_number,
                    session_key=request.session.session_key,
                    user__isnull=True
                )
            
            serializer = OrderDetailSerializer(order)
            return success_response(
                data=serializer.data,
                message="Order details retrieved successfully"
            )
        
        except Order.DoesNotExist:
            return not_found_response(message="Order not found")


class CreateOrderView(APIView):
    """
    POST /api/orders/create/ - Create order from cart
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Create order from cart"""
        serializer = CreateOrderSerializer(data=request.data, context={'request': request})
        
        if not serializer.is_valid():
            return bad_request_response(
                message="Invalid data",
                errors=serializer.errors
            )
        
        # Get cart
        cart = self._get_cart(request)
        
        if not cart:
            return bad_request_response(message="Cart not found")
        
        if cart.items.count() == 0:
            return bad_request_response(message="Cart is empty")
        
        # Validate stock availability
        for item in cart.items.all():
            available_stock = item.get_stock()
            if item.quantity > available_stock:
                return bad_request_response(
                    message=f"Insufficient stock for {item.get_display_name()}. Only {available_stock} available."
                )
        
        try:
            with transaction.atomic():
                # Handle addresses differently for authenticated vs guest users
                if request.user.is_authenticated:
                    # For authenticated users: create Address objects
                    billing_address = self._get_or_create_address(
                        request,
                        serializer.validated_data.get('billing_address_id'),
                        serializer.validated_data.get('guest_billing_address'),
                        'billing'
                    )
                    
                    shipping_address = self._get_or_create_address(
                        request,
                        serializer.validated_data.get('shipping_address_id'),
                        serializer.validated_data.get('guest_shipping_address'),
                        'shipping'
                    )
                    
                    guest_billing_data = None
                    guest_shipping_data = None
                else:
                    # For guest users: use JSON data, don't create Address objects
                    billing_address = None
                    shipping_address = None
                    guest_billing_data = serializer.validated_data.get('guest_billing_address')
                    guest_shipping_data = serializer.validated_data.get('guest_shipping_address')
                
                # Calculate shipping cost based on city
                provided_shipping_cost = serializer.validated_data.get('shipping_cost')
                if provided_shipping_cost is not None and provided_shipping_cost > 0:
                    shipping_cost = provided_shipping_cost
                else:
                    # Auto-calculate based on city from shipping address
                    if shipping_address:
                        shipping_cost = self._calculate_shipping_cost_from_address(shipping_address)
                    elif guest_shipping_data:
                        shipping_cost = self._calculate_shipping_cost_from_data(guest_shipping_data)
                    else:
                        shipping_cost = 120  # Default outside Dhaka
                
                # Calculate totals
                subtotal = cart.get_subtotal()
                discount = serializer.validated_data.get('discount', 0)
                total_price = subtotal - discount + shipping_cost
                
                # Create order
                order = Order.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    session_key=cart.session_key if not request.user.is_authenticated else None,
                    billing_address=billing_address,
                    shipping_address=shipping_address,
                    guest_email=serializer.validated_data.get('guest_email'),
                    guest_phone=serializer.validated_data.get('guest_phone'),
                    guest_billing_address_data=guest_billing_data,
                    guest_shipping_address_data=guest_shipping_data,
                    subtotal=subtotal,
                    discount=discount,
                    shipping_cost=shipping_cost,
                    total_price=total_price,
                    notes=serializer.validated_data.get('notes', '')
                )
                
                # Create order items
                for cart_item in cart.items.all():
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product if cart_item.product else (cart_item.variant.product if cart_item.variant else None),
                        variant=cart_item.variant,
                        product_title=cart_item.product_title,
                        variant_sku=cart_item.variant_sku,
                        variant_attributes=cart_item.variant_attributes,
                        quantity=cart_item.quantity,
                        unit_price=cart_item.price_snapshot,
                        subtotal=cart_item.get_total()
                    )
                    
                    # Reduce stock
                    if cart_item.variant:
                        cart_item.variant.stock -= cart_item.quantity
                        cart_item.variant.save()
                    elif cart_item.product:
                        cart_item.product.stock -= cart_item.quantity
                        cart_item.product.save()
                
                # Create payment record
                Payment.objects.create(
                    order=order,
                    method=serializer.validated_data.get('payment_method', 'cod'),
                    amount=total_price,
                    success=False  # Will be updated when payment is confirmed
                )
                
                # Clear cart
                cart.items.all().delete()
                
                # Return order details
                order_serializer = OrderDetailSerializer(order)
                return created_response(
                    data=order_serializer.data,
                    message="Order created successfully"
                )
        
        except Exception as e:
            return error_response(
                message=f"Failed to create order: {str(e)}",
                status_code=500
            )
    
    def _get_cart(self, request):
        """Get cart for authenticated user or guest"""
        if request.user.is_authenticated:
            return Cart.objects.filter(user=request.user).first()
        else:
            if not request.session.session_key:
                return None
            return Cart.objects.filter(
                session_key=request.session.session_key,
                user__isnull=True
            ).first()
    
    def _get_or_create_address(self, request, address_id, guest_address_data, address_type):
        """Get existing address or create temporary one for guest"""
        if address_id and request.user.is_authenticated:
            # Use existing address for authenticated user
            try:
                return Address.objects.get(id=address_id, user=request.user)
            except Address.DoesNotExist:
                raise ValueError(f"{address_type.capitalize()} address not found")
        
        elif guest_address_data:
            # Create temporary address (not linked to any user for guests)
            address = Address.objects.create(
                user=request.user if request.user.is_authenticated else None,
                address_type=address_type,
                label=guest_address_data.get('label', 'Guest Address'),
                phone=guest_address_data['phone'],
                street=guest_address_data['street'],
                city=guest_address_data['city'],
                state=guest_address_data['state'],
                postal_code=guest_address_data['postal_code'],
                country=guest_address_data.get('country', 'Bangladesh'),
                is_default_billing=False,
                is_default_shipping=False
            )
            return address
        
        raise ValueError(f"{address_type.capitalize()} address is required")
    
    def _calculate_shipping_cost_from_address(self, shipping_address):
        """
        Calculate shipping cost based on Address object
        Dhaka: 60 TK
        Outside Dhaka: 120 TK
        """
        city = shipping_address.city.strip().lower()
        
        # Check if city is Dhaka (case-insensitive)
        if city == 'dhaka':
            return 60
        else:
            return 120
    
    def _calculate_shipping_cost_from_data(self, shipping_data):
        """
        Calculate shipping cost based on address data dictionary
        Dhaka: 60 TK
        Outside Dhaka: 120 TK
        """
        city = shipping_data.get('city', '').strip().lower()
        
        # Check if city is Dhaka (case-insensitive)
        if city == 'dhaka':
            return 60
        else:
            return 120


class CancelOrderView(APIView):
    """
    PATCH /api/orders/{order_number}/cancel/ - Cancel an order
    """
    permission_classes = [AllowAny]
    
    def patch(self, request, order_number):
        """Cancel an order"""
        try:
            if request.user.is_authenticated:
                order = Order.objects.get(
                    order_number=order_number,
                    user=request.user
                )
            else:
                if not request.session.session_key:
                    return not_found_response(message="Order not found")
                
                order = Order.objects.get(
                    order_number=order_number,
                    session_key=request.session.session_key,
                    user__isnull=True
                )
            
            # Check if order can be cancelled
            if order.status in ['shipped', 'delivered', 'cancelled']:
                return bad_request_response(
                    message=f"Cannot cancel order with status: {order.status}"
                )
            
            if order.payment_status == 'paid':
                return bad_request_response(
                    message="Cannot cancel paid order. Please contact support for refund."
                )
            
            with transaction.atomic():
                # Restore stock
                for item in order.items.all():
                    if item.variant:
                        item.variant.stock += item.quantity
                        item.variant.save()
                    elif item.product:
                        item.product.stock += item.quantity
                        item.product.save()
                
                # Update order status
                order.status = 'cancelled'
                order.payment_status = 'failed'
                order.save()
            
            serializer = OrderDetailSerializer(order)
            return success_response(
                data=serializer.data,
                message="Order cancelled successfully"
            )
        
        except Order.DoesNotExist:
            return not_found_response(message="Order not found")
