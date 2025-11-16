from django.contrib import admin
from django.utils.html import format_html
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    """Inline to show cart items inside a cart."""
    model = CartItem
    extra = 0
    fields = ['variant', 'quantity', 'price_snapshot', 'get_total']
    readonly_fields = ['get_total']

    def get_total(self, obj):
        """Show total price for this item."""
        return f"৳{obj.get_total():,.2f}"
    get_total.short_description = 'Total'


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Simplified Cart admin."""
    list_display = ['id', 'get_owner', 'get_total_items', 'get_subtotal', 'updated_at']
    search_fields = ['user__email', 'session_key']
    readonly_fields = ['get_total_items', 'get_subtotal', 'created_at', 'updated_at']
    inlines = [CartItemInline]
    date_hierarchy = 'created_at'

    actions = ['clear_selected_carts', 'delete_empty_carts']

    def get_owner(self, obj):
        """Display cart owner or guest."""
        if obj.user:
            return obj.user.email
        return f"Guest ({obj.session_key[:8]}...)" if obj.session_key else "Anonymous"
    get_owner.short_description = 'Owner'

    def get_total_items(self, obj):
        """Total items in cart."""
        return obj.get_total_items()
    get_total_items.short_description = 'Items'

    def get_subtotal(self, obj):
        """Subtotal of all cart items."""
        return f"৳{obj.get_subtotal():,.2f}"
    get_subtotal.short_description = 'Subtotal'

    def clear_selected_carts(self, request, queryset):
        """Remove all items from selected carts."""
        count = sum(cart.items.count() for cart in queryset)
        for cart in queryset:
            cart.clear()
        self.message_user(request, f"Cleared {count} items from {queryset.count()} cart(s).")
    clear_selected_carts.short_description = "Clear selected carts"

    def delete_empty_carts(self, request, queryset):
        """Delete carts with no items."""
        empty_carts = queryset.filter(items__isnull=True)
        count = empty_carts.count()
        empty_carts.delete()
        self.message_user(request, f"Deleted {count} empty cart(s).")
    delete_empty_carts.short_description = "Delete empty carts"


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Simplified CartItem admin."""
    list_display = ['id', 'get_cart_owner', 'variant', 'quantity', 'price_snapshot', 'get_total', 'added_at']
    search_fields = ['variant__product__title', 'cart__user__email']
    readonly_fields = ['get_total', 'added_at', 'updated_at']

    def get_cart_owner(self, obj):
        """Cart owner display."""
        return obj.cart.user.email if obj.cart.user else f"Guest ({obj.cart.session_key[:8]}...)"
    get_cart_owner.short_description = 'Cart Owner'

    def get_total(self, obj):
        """Display total for cart item."""
        return f"৳{obj.get_total():,.2f}"
    get_total.short_description = 'Total'
