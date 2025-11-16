"""
API Views for cart management
"""
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.db import transaction

from cart.models import Cart, CartItem
from catalog.models import ProductVariant, Product
from api.serializers import (
    CartSerializer,
    CartItemSerializer,
    AddToCartSerializer,
    UpdateCartItemSerializer,
)
from api.utils import success_response, error_response, created_response, not_found_response, bad_request_response


class CartView(APIView):
    """
    GET /api/cart/
    Get current user's cart (or guest cart)
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get cart for authenticated user or guest"""
        cart = self._get_or_create_cart(request)
        # Prefetch related data for images
        cart = Cart.objects.prefetch_related(
            'items__variant__product__images',
            'items__product__images'
        ).get(pk=cart.pk)
        serializer = CartSerializer(cart)
        
        response_data = serializer.data
        # Add debug info
        response_data['debug'] = {
            'cart_id': cart.id,
            'session_key': request.session.session_key,
            'is_authenticated': request.user.is_authenticated,
            'items_count': cart.items.count(),
        }
        
        return success_response(
            data=response_data,
            message="Cart retrieved successfully"
        )
    
    def _get_or_create_cart(self, request):
        """Get or create cart for user or guest"""
        if request.user.is_authenticated:
            # Get or create cart for authenticated user
            cart, created = Cart.objects.get_or_create(user=request.user)
            
            # Merge guest cart if exists
            session_key = request.session.session_key
            if session_key:
                guest_cart = Cart.objects.filter(
                    session_key=session_key,
                    user__isnull=True
                ).first()
                
                if guest_cart:
                    self._merge_carts(guest_cart, cart)
        else:
            # Get or create cart for guest using session
            if not request.session.session_key:
                request.session.create()
                request.session.save()  # Save the session to persist it
            
            session_key = request.session.session_key
            cart, created = Cart.objects.get_or_create(
                session_key=session_key,
                user__isnull=True
            )
        
        return cart
    
    def _merge_carts(self, guest_cart, user_cart):
        """Merge guest cart into user cart"""
        with transaction.atomic():
            for guest_item in guest_cart.items.all():
                # Check if user cart already has this variant
                user_item = user_cart.items.filter(
                    variant=guest_item.variant
                ).first()
                
                if user_item:
                    # Update quantity (add guest quantity to user quantity)
                    user_item.quantity += guest_item.quantity
                    user_item.save()
                else:
                    # Move item to user cart
                    guest_item.cart = user_cart
                    guest_item.save()
            
            # Delete guest cart
            guest_cart.delete()


class AddToCartView(APIView):
    """
    POST /api/cart/items/
    Add item to cart
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Add product variant or base product to cart"""
        serializer = AddToCartSerializer(data=request.data)
        
        if not serializer.is_valid():
            return bad_request_response(
                message="Invalid data",
                errors=serializer.errors
            )
        
        variant_id = serializer.validated_data.get('variant_id')
        product_id = serializer.validated_data.get('product_id')
        quantity = serializer.validated_data['quantity']
        
        variant = None
        product = None
        effective_price = None
        stock = 0
        
        # Handle variant-based products
        if variant_id:
            try:
                variant = ProductVariant.objects.select_related('product').get(id=variant_id)
                effective_price = variant.sale_price if variant.sale_price else variant.price
                stock = variant.stock
            except ProductVariant.DoesNotExist:
                return not_found_response(message="Variant not found")
        
        # Handle non-variant products
        elif product_id:
            try:
                product = Product.objects.get(id=product_id)
                effective_price = product.sale_price if product.sale_price else product.price
                stock = product.stock
            except Product.DoesNotExist:
                return not_found_response(message="Product not found")
        
        # Check stock availability
        if quantity > stock:
            return bad_request_response(
                message=f"Only {stock} items available in stock"
            )
        
        # Get or create cart
        cart = self._get_or_create_cart(request)
        
        # Check if item already in cart and update accordingly
        if variant:
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                variant=variant,
                defaults={
                    'quantity': quantity,
                    'price_snapshot': effective_price
                }
            )
        else:  # product
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={
                    'quantity': quantity,
                    'price_snapshot': effective_price
                }
            )
        
        if not created:
            # Update quantity if item already exists
            new_quantity = cart_item.quantity + quantity
            
            # Check stock for new quantity
            if new_quantity > stock:
                return bad_request_response(
                    message=f"Only {stock} items available in stock"
                )
            
            cart_item.quantity = new_quantity
            cart_item.save()
        
        # Return cart item data with debug info
        item_serializer = CartItemSerializer(cart_item)
        response_data = item_serializer.data
        
        # Add debug info to help troubleshoot guest cart issues
        response_data['debug'] = {
            'cart_id': cart.id,
            'session_key': request.session.session_key,
            'is_authenticated': request.user.is_authenticated,
        }
        
        return created_response(
            data=response_data,
            message="Item added to cart successfully"
        )
    
    def _get_or_create_cart(self, request):
        """Get or create cart for user or guest"""
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
        else:
            if not request.session.session_key:
                request.session.create()
                request.session.save()  # Save the session to persist it
            
            session_key = request.session.session_key
            cart, created = Cart.objects.get_or_create(
                session_key=session_key,
                user__isnull=True
            )
        
        return cart


class UpdateCartItemView(APIView):
    """
    PATCH /api/cart/items/{id}/ - Update cart item quantity
    DELETE /api/cart/items/{id}/ - Remove cart item
    """
    permission_classes = [AllowAny]
    
    def patch(self, request, pk):
        """Update cart item quantity"""
        serializer = UpdateCartItemSerializer(data=request.data)
        
        if not serializer.is_valid():
            return bad_request_response(
                message="Invalid data",
                errors=serializer.errors
            )
        
        quantity = serializer.validated_data['quantity']
        
        # Get cart item
        try:
            cart_item = self._get_cart_item(request, pk)
        except CartItem.DoesNotExist:
            return not_found_response(message="Cart item not found")
        
        # Check stock availability
        stock = cart_item.get_stock()
        if quantity > stock:
            return bad_request_response(
                message=f"Only {stock} items available in stock"
            )
        
        # Update quantity
        cart_item.quantity = quantity
        cart_item.save()
        
        # Return updated cart item
        item_serializer = CartItemSerializer(cart_item)
        return success_response(
            data=item_serializer.data,
            message="Cart item updated successfully"
        )
    
    def delete(self, request, pk):
        """Remove cart item"""
        try:
            cart_item = self._get_cart_item(request, pk)
            cart_item.delete()
            return success_response(
                message="Cart item removed successfully",
                status_code=200
            )
        except CartItem.DoesNotExist:
            return not_found_response(message="Cart item not found")
    
    def _get_cart_item(self, request, pk):
        """Get cart item for current user/guest"""
        if request.user.is_authenticated:
            return CartItem.objects.select_related('variant', 'cart').get(
                id=pk,
                cart__user=request.user
            )
        else:
            session_key = request.session.session_key
            if not session_key:
                raise CartItem.DoesNotExist
            
            return CartItem.objects.select_related('variant', 'cart').get(
                id=pk,
                cart__session_key=session_key,
                cart__user__isnull=True
            )


# Keep RemoveCartItemView as alias for backwards compatibility
RemoveCartItemView = UpdateCartItemView


class ClearCartView(APIView):
    """
    DELETE /api/cart/clear/
    Clear all items from cart
    """
    permission_classes = [AllowAny]
    
    def delete(self, request):
        """Clear all items from cart"""
        cart = self._get_cart(request)
        
        if cart:
            cart.clear()
            return success_response(
                message="Cart cleared successfully"
            )
        
        return success_response(
            message="Cart is already empty"
        )
    
    def _get_cart(self, request):
        """Get cart for current user/guest"""
        if request.user.is_authenticated:
            return Cart.objects.filter(user=request.user).first()
        else:
            session_key = request.session.session_key
            if not session_key:
                return None
            
            return Cart.objects.filter(
                session_key=session_key,
                user__isnull=True
            ).first()
