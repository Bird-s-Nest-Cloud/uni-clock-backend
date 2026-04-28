from cart.models import Cart
from django.db import transaction

class CartMixin:
    """
    Mixin to provide shared cart logic for API views
    """
    
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
            # Fallback to header if session cookie is blocked
            session_key = request.headers.get('X-Session-ID') or request.session.session_key
            
            if not session_key:
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
                # Check if user cart already has this variant/product
                if guest_item.variant:
                    user_item = user_cart.items.filter(
                        variant=guest_item.variant
                    ).first()
                else:
                    user_item = user_cart.items.filter(
                        product=guest_item.product
                    ).first()
                
                if user_item:
                    # Update quantity (add guest quantity to user quantity)
                    user_item.quantity += guest_item.quantity
                    user_item.save()
                    guest_item.delete()
                else:
                    # Move item to user cart
                    guest_item.cart = user_cart
                    guest_item.save()
            
            # Delete guest cart after merging
            guest_cart.delete()
