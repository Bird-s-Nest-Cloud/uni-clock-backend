from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils import timezone
from accounts.models import Address
from catalog.models import ProductVariant, Product
from cart.models import Cart, CartItem


User = settings.AUTH_USER_MODEL
# Create your models here.


class Order(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders',
        null=True,
        blank=True,
        help_text='May be null for guest orders'
    )


    session_key = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        db_index=True,
        help_text='Session ID for anonymous users'
    )

    order_number = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        verbose_name='Order Number'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='unpaid'
    )

    billing_address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        related_name='billing_orders',
        blank=True,
        null=True
    )

    shipping_address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        related_name='shipping_orders',
        blank=True,
        null=True
    )
    
    # Guest address fields (JSON) - for orders without registered user
    guest_email = models.EmailField(max_length=255, blank=True, null=True, help_text='Email for guest orders')
    guest_phone = models.CharField(max_length=20, blank=True, null=True, help_text='Phone for guest orders')
    guest_billing_address_data = models.JSONField(blank=True, null=True, help_text='Billing address for guest orders')
    guest_shipping_address_data = models.JSONField(blank=True, null=True, help_text='Shipping address for guest orders')

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)]  
    )

    discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
    )

    shipping_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
    )

    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)]
    )

    notes = models.TextField(
        blank=True,
        help_text='Additional notes or instructions for the order'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'orders'
        ordering = ['-created_at']

    def __str__(self):
        return self.order_number
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            prefix = "ORD"
            last_order = Order.objects.order_by('-id').first()
            next_id = 1 if not last_order else last_order.id + 1
            self.order_number = f"{prefix}-{next_id}"
        super().save(*args, **kwargs)

    def get_total_items(self):
        return sum(item.quantity for item in self.items.all())
    
    @staticmethod
    def create_from_cart(cart, billing_address=None, shipping_address=None, discount=0, shipping_cost=0):

        user = cart.user if cart.user else None

        subtotal = cart.get_subtotal()
        total_price = subtotal - discount + shipping_cost

        order = Order.objects.create(
            user=user,
            session_key=cart.session_key,
            billing_address=billing_address,
            shipping_address=shipping_address,
            subtotal=subtotal,
            discount=discount,
            shipping_cost=shipping_cost,
            total_price=total_price
        )

        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.variant.product if item.variant else None,
                variant=item.variant,
                product_title=item.product_title,
                variant_sku=item.variant_sku,
                variant_attributes=item.variant_attributes,
                quantity=item.quantity,
                unit_price=item.price_snapshot,
                subtotal=item.get_total()
            )

        cart.clear()
        return order
    

class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    product_title = models.CharField(max_length=255, blank=True)
    variant_sku = models.CharField(max_length=100, blank=True)
    variant_attributes = models.CharField(max_length=255, blank=True)

    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'order_items'
        ordering = ['order']

    def __str__(self):
        return f"{self.product_title} x {self.quantity}"
    

class Payment (models.Model):

    METHOD_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('card', 'Credit/Debit Card'),
        ('bkash', 'bKash'),
        ('nagad', 'Nagad'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default='cod')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    paid_at = models.DateTimeField(null=True, blank=True)
    success = models.BooleanField(default=False)

    class Meta:
        db_table = 'payments'
        ordering = ['-paid_at']

    def __str__(self):
        return f"Payment for Order #{self.order.order_number}"
    
    def mark_as_paid(self, transaction_id=None):
        """Mark payment as successful and update order status."""
        self.success = True
        self.transaction_id = transaction_id or self.transaction_id
        self.paid_at = timezone.now()
        self.save()
        self.order.payment_status = 'paid'
        self.order.save()

