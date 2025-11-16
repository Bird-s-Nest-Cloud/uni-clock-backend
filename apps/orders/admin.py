from django.contrib import admin
from django.utils.html import format_html
import json
from .models import Order, OrderItem, Payment
# Register your models here.

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_title', 'variant_sku', 'quantity', 'unit_price', 'subtotal')


@admin.register(Order)
class OrderAdmin (admin.ModelAdmin):
    list_display = ('order_number', 'user', 'guest_email', 'status', 'payment_status', 'total_price', 'created_at')
    list_filter = ('status', 'payment_status', 'created_at')
    search_fields = ('order_number', 'user__email', 'user__name', 'guest_email', 'guest_phone')
    readonly_fields = (
        'order_number', 'created_at', 'updated_at', 'subtotal', 'total_price',
        'display_customer_info', 'display_billing_address', 'display_shipping_address'
    )
    inlines = [OrderItemInline]
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'status', 'payment_status', 'session_key')
        }),
        ('Customer & Shipping Information', {
            'fields': ('display_customer_info', 'display_billing_address', 'display_shipping_address'),
            'description': 'Customer details and delivery addresses'
        }),
        ('Pricing', {
            'fields': ('subtotal', 'shipping_cost', 'discount_amount', 'total_price')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def display_customer_info(self, obj):
        """Display customer information for both authenticated and guest users"""
        if obj.user:
            # For authenticated users
            user = obj.user
            html = f"""
            <div style="line-height: 1.8; padding: 10px; background-color: #f8f9fa; border-radius: 5px;">
                <strong style="color: #0066cc;">Registered User</strong><br>
                <strong>Name:</strong> {user.name if hasattr(user, 'name') else 'N/A'}<br>
                <strong>Email:</strong> {user.email}<br>
                <strong>Phone:</strong> {user.phone if hasattr(user, 'phone') else 'N/A'}<br>
                <strong>User ID:</strong> {user.id}
            </div>
            """
            return format_html(html)
        elif obj.guest_email:
            # For guest users
            html = f"""
            <div style="line-height: 1.8; padding: 10px; background-color: #fff3cd; border-radius: 5px;">
                <strong style="color: #856404;">Guest User</strong><br>
                <strong>Email:</strong> {obj.guest_email}<br>
                <strong>Phone:</strong> {obj.guest_phone or 'N/A'}<br>
                <strong>Session:</strong> {obj.session_key[:20]}... (guest order)
            </div>
            """
            return format_html(html)
        return format_html('<div style="color: #dc3545;">No customer information available</div>')
    
    display_customer_info.short_description = "Customer Details"
    
    def display_billing_address(self, obj):
        """Display billing address in a readable format"""
        if obj.billing_address:
            # For authenticated users with Address model
            addr = obj.billing_address
            html = f"""
            <div style="line-height: 1.6;">
                <strong>{addr.label}</strong><br>
                {addr.street}<br>
                {addr.city}, {addr.state} {addr.postal_code}<br>
                {addr.country}<br>
                Phone: {addr.phone}
            </div>
            """
            return format_html(html)
        elif obj.guest_billing_address_data:
            # For guest users with JSON data
            addr = obj.guest_billing_address_data
            html = f"""
            <div style="line-height: 1.6;">
                <strong>{addr.get('label', 'N/A')}</strong><br>
                {addr.get('street', 'N/A')}<br>
                {addr.get('city', 'N/A')}, {addr.get('state', 'N/A')} {addr.get('postal_code', 'N/A')}<br>
                {addr.get('country', 'N/A')}<br>
                Phone: {addr.get('phone', 'N/A')}
            </div>
            """
            return format_html(html)
        return "No billing address"
    
    display_billing_address.short_description = "Billing Address"
    
    def display_shipping_address(self, obj):
        """Display shipping address in a readable format"""
        if obj.shipping_address:
            # For authenticated users with Address model
            addr = obj.shipping_address
            html = f"""
            <div style="line-height: 1.6;">
                <strong>{addr.label}</strong><br>
                {addr.street}<br>
                {addr.city}, {addr.state} {addr.postal_code}<br>
                {addr.country}<br>
                Phone: {addr.phone}
            </div>
            """
            return format_html(html)
        elif obj.guest_shipping_address_data:
            # For guest users with JSON data
            addr = obj.guest_shipping_address_data
            html = f"""
            <div style="line-height: 1.6;">
                <strong>{addr.get('label', 'N/A')}</strong><br>
                {addr.get('street', 'N/A')}<br>
                {addr.get('city', 'N/A')}, {addr.get('state', 'N/A')} {addr.get('postal_code', 'N/A')}<br>
                {addr.get('country', 'N/A')}<br>
                Phone: {addr.get('phone', 'N/A')}
            </div>
            """
            return format_html(html)
        return "No shipping address"
    
    display_shipping_address.short_description = "Shipping Address"

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'method', 'amount', 'success', 'paid_at')
    list_filter = ('method', 'success')
    search_fields = ('order__order_number', 'transaction_id')