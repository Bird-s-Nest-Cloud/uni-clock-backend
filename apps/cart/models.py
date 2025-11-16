from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings
from catalog.models import ProductVariant, Product


class Cart(models.Model):
    """
    Shopping cart - can belong to user or be anonymous (session-based).
    From SRS Section 10: cart_id, user_id (nullable), session_key (nullable)
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='carts',
        help_text='Cart owner (null for guest carts)'
    )
    
    session_key = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        db_index=True,
        help_text='Session ID for anonymous users'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'carts'
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'
        ordering = ['-updated_at']
    
    def __str__(self):
        if self.user:
            return f"Cart - {self.user.email}"
        return f"Cart - Guest ({self.session_key[:8]}...)"
    
    def get_total_items(self):
        """Get total number of items in cart."""
        return sum(item.quantity for item in self.items.all())
    
    def get_subtotal(self):
        """Calculate cart subtotal (before shipping/tax)."""
        return sum(item.get_total() for item in self.items.all())
    
    def get_total_savings(self):
        """Calculate total savings from discounts."""
        return sum(item.get_savings() for item in self.items.all())
    
    def clear(self):
        """Remove all items from cart."""
        self.items.all().delete()


class CartItem(models.Model):
    """
    Individual items in cart.
    Supports both products with variants and products without variants.
    """
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )
    
    # For products WITH variants
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cart_items',
        help_text='Product variant (for products with variants)'
    )
    
    # For products WITHOUT variants
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cart_items',
        help_text='Base product (for products without variants)'
    )

    # Store variant details in case variant is deleted
    variant_sku = models.CharField(
        max_length=100,
        blank=True,
        help_text='Backup SKU in case variant is deleted'
    )
    
    product_title = models.CharField(
        max_length=255,
        blank=True,
        help_text='Backup product title'
    )
    
    variant_attributes = models.CharField(
        max_length=255,
        blank=True,
        help_text='Backup variant attributes (e.g., Red / Medium)'
    )
    
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text='Quantity of this item'
    )
    
    # Price snapshot - store price at time of adding to cart
    # In case product price changes later
    price_snapshot = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Price when added to cart'
    )
    
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cart_items'
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        # Ensure uniqueness: one variant OR one product per cart
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(variant__isnull=False, product__isnull=True) |
                    models.Q(variant__isnull=True, product__isnull=False)
                ),
                name='cart_item_variant_or_product'
            ),
            models.UniqueConstraint(
                fields=['cart', 'variant'],
                condition=models.Q(variant__isnull=False),
                name='unique_cart_variant'
            ),
            models.UniqueConstraint(
                fields=['cart', 'product'],
                condition=models.Q(product__isnull=False),
                name='unique_cart_product'
            ),
        ]
        ordering = ['added_at']
    
    def __str__(self):
        if self.variant and hasattr(self.variant, 'product'):
            return f"{self.variant.product.title} ({self.variant.sku}) x {self.quantity}"
        elif self.product:
            return f"{self.product.title} x {self.quantity}"
        return f"{self.product_title} ({self.variant_sku}) x {self.quantity}"
    
    def save(self, *args, **kwargs):
        """Set price snapshot and backup data on first save."""
        # Handle variant-based products
        if self.variant:
            if not self.price_snapshot:
                self.price_snapshot = self.variant.get_effective_price()

            # Store backup data
            self.variant_sku = self.variant.sku
            if hasattr(self.variant, 'product') and self.variant.product:
                self.product_title = self.variant.product.title
            self.variant_attributes = self.variant.get_attributes_display()
        
        # Handle non-variant products
        elif self.product:
            if not self.price_snapshot:
                # Use sale price if available, else regular price
                self.price_snapshot = self.product.sale_price or self.product.price
            
            # Store backup data
            self.product_title = self.product.title
            self.variant_sku = f"PROD-{self.product.id}"
            self.variant_attributes = ""

        super().save(*args, **kwargs)
    
    def get_total(self):
        """Get total price for this cart item (quantity × price)."""
        if self.price_snapshot is None:
            return 0
        return self.price_snapshot * self.quantity
    
    def get_savings(self):
        """Calculate savings if variant/product is on sale."""
        if self.variant and self.variant.is_on_sale():
            original = self.variant.price
            discount = original - self.variant.sale_price
            return discount * self.quantity
        elif self.product and self.product.sale_price:
            original = self.product.price
            discount = original - self.product.sale_price
            return discount * self.quantity
        return 0
    
    def is_price_changed(self):
        """Check if current variant/product price differs from snapshot."""
        if self.variant:
            current_price = self.variant.get_effective_price()
        elif self.product:
            current_price = self.product.sale_price or self.product.price
        else:
            return False
        return current_price != self.price_snapshot
    
    def update_price_snapshot(self):
        """Update price snapshot to current price."""
        if self.variant:
            self.price_snapshot = self.variant.get_effective_price()
        elif self.product:
            self.price_snapshot = self.product.sale_price or self.product.price
        self.save()

    def is_available(self):
        """Check if variant/product still exists and is in stock."""
        if self.variant:
            return self.variant.is_active and self.variant.is_in_stock()
        elif self.product:
            return self.product.is_active and self.product.stock > 0
        return False
    

    def get_display_title(self):
        """Get display title for the cart item."""
        if self.variant:
            attributes = self.variant.get_attributes_display()
            if attributes:
                return f"{self.variant.product.title} ({attributes})"
            return self.variant.product.title
        elif self.product:
            return self.product.title
        
        # Fallback to stored data
        if self.variant_attributes:
            return f"{self.product_title} ({self.variant_attributes})"
        return self.product_title
    
    def get_stock(self):
        """Get available stock for this item."""
        if self.variant:
            return self.variant.stock
        elif self.product:
            return self.product.stock
        return 0