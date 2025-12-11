from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Banner, FeaturedSection


# Register your models here.


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    """
    Admin interface for Banner model with image preview and status indicators.
    """
    list_display = (
        'title',
        'image_preview',
        'linked_product',
        'authentic',
        'display_order',
        'status_indicator',
        'schedule_info',
        'created_at'
    )
    
    list_filter = (
        'is_active',
        'authentic',
        'created_at',
        'start_date',
        'end_date'
    )
    
    search_fields = (
        'title',
        'subtitle',
        'link_product__name',
        'button_text'
    )
    
    readonly_fields = (
        'created_at',
        'updated_at',
        'image_preview_large',
        'mobile_image_preview_large',
        'current_status'
    )
    
    fieldsets = (
        ('Banner Content', {
            'fields': (
                'title',
                'subtitle',
                'button_text'
            )
        }),
        ('Images', {
            'fields': (
                'image',
                'image_preview_large',
                'mobile_image',
                'mobile_image_preview_large'
            )
        }),
        ('Link Configuration', {
            'fields': (
                'link_product',
            )
        }),
        ('Display Settings', {
            'fields': (
                'display_order',
                'is_active',
                'authentic',
                'current_status'
            )
        }),
        ('Scheduling (Optional)', {
            'fields': (
                'start_date',
                'end_date'
            ),
            'description': 'Set dates to automatically activate/deactivate the banner'
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        })
    )
    
    ordering = ('display_order', '-created_at')
    
    list_per_page = 20
    
    def image_preview(self, obj):
        """Display thumbnail preview in list view"""
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 100px; height: 50px; object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return '-'
    image_preview.short_description = 'Preview'
    
    def image_preview_large(self, obj):
        """Display larger image preview in detail view"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 600px; max-height: 300px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />',
                obj.image.url
            )
        return 'No image uploaded'
    image_preview_large.short_description = 'Desktop Image Preview'
    
    def mobile_image_preview_large(self, obj):
        """Display larger mobile image preview in detail view"""
        if obj.mobile_image:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 400px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />',
                obj.mobile_image.url
            )
        return 'No mobile image uploaded (will use desktop image)'
    mobile_image_preview_large.short_description = 'Mobile Image Preview'
    
    def linked_product(self, obj):
        """Display linked product name"""
        if obj.link_product:
            return obj.link_product.name
        return '-'
    linked_product.short_description = 'Linked Product'
    
    def status_indicator(self, obj):
        """Display visual status indicator"""
        if obj.is_currently_active():
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">● Active</span>'
            )
        elif obj.is_active:
            return format_html(
                '<span style="color: #ffc107; font-weight: bold;">● Scheduled</span>'
            )
        else:
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">● Inactive</span>'
            )
    status_indicator.short_description = 'Status'
    
    def current_status(self, obj):
        """Display detailed current status"""
        if obj.is_currently_active():
            return format_html(
                '<span style="color: #28a745; font-weight: bold; font-size: 14px;">✓ Currently Active and Visible</span>'
            )
        elif obj.is_active:
            now = timezone.now()
            if obj.start_date and now < obj.start_date:
                return format_html(
                    '<span style="color: #ffc107; font-weight: bold;">⏳ Scheduled to start on {}</span>',
                    obj.start_date.strftime('%Y-%m-%d %H:%M')
                )
            elif obj.end_date and now > obj.end_date:
                return format_html(
                    '<span style="color: #dc3545; font-weight: bold;">⏹ Ended on {}</span>',
                    obj.end_date.strftime('%Y-%m-%d %H:%M')
                )
        return format_html(
            '<span style="color: #dc3545; font-weight: bold;">✗ Inactive</span>'
        )
    current_status.short_description = 'Current Status'
    
    def schedule_info(self, obj):
        """Display scheduling information"""
        if obj.start_date or obj.end_date:
            info = []
            if obj.start_date:
                info.append(f"Start: {obj.start_date.strftime('%Y-%m-%d')}")
            if obj.end_date:
                info.append(f"End: {obj.end_date.strftime('%Y-%m-%d')}")
            return ' | '.join(info)
        return 'Always Active'
    schedule_info.short_description = 'Schedule'
    
    actions = ['activate_banners', 'deactivate_banners']
    
    def activate_banners(self, request, queryset):
        """Bulk action to activate selected banners"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} banner(s) activated successfully.')
    activate_banners.short_description = 'Activate selected banners'
    
    def deactivate_banners(self, request, queryset):
        """Bulk action to deactivate selected banners"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} banner(s) deactivated successfully.')
    deactivate_banners.short_description = 'Deactivate selected banners'


@admin.register(FeaturedSection)
class FeaturedSectionAdmin(admin.ModelAdmin):
    """
    Admin interface for FeaturedSection model with product selection and preview.
    """
    list_display = (
        'title',
        'section_type',
        'product_count_display',
        'max_products',
        'display_order',
        'is_active',
        'created_at'
    )
    
    list_filter = (
        'section_type',
        'is_active',
        'created_at',
        'category'
    )
    
    search_fields = (
        'title',
        'subtitle',
        'category__name'
    )
    
    readonly_fields = (
        'created_at',
        'updated_at',
        'product_preview',
        'product_count_info'
    )
    
    filter_horizontal = ('products',)
    
    fieldsets = (
        ('Section Information', {
            'fields': (
                'title',
                'subtitle'
            )
        }),
        ('Product Selection', {
            'fields': (
                'section_type',
                'category',
                'products',
                'max_products'
            ),
            'description': 'Configure how products are selected for this section'
        }),
        ('Display Settings', {
            'fields': (
                'display_order',
                'is_active'
            )
        }),
        ('Preview & Statistics', {
            'fields': (
                'product_count_info',
                'product_preview'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        })
    )
    
    ordering = ('display_order', '-created_at')
    
    list_per_page = 20
    
    def product_count_display(self, obj):
        """Display product count with color coding"""
        count = obj.get_products().count()
        if count == 0:
            color = '#dc3545'  # Red
            icon = '⚠'
        elif count < obj.max_products:
            color = '#ffc107'  # Yellow
            icon = '◐'
        else:
            color = '#28a745'  # Green
            icon = '✓'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {} products</span>',
            color, icon, count
        )
    product_count_display.short_description = 'Products'
    
    def product_count_info(self, obj):
        """Display detailed product count information"""
        count = obj.get_products().count()
        max_count = obj.max_products
        
        if count == 0:
            return format_html(
                '<span style="color: #dc3545; font-weight: bold; font-size: 14px;">⚠ No products will be displayed</span>'
            )
        elif count < max_count:
            return format_html(
                '<span style="color: #ffc107; font-weight: bold; font-size: 14px;">◐ {} of {} products available</span>',
                count, max_count
            )
        else:
            return format_html(
                '<span style="color: #28a745; font-weight: bold; font-size: 14px;">✓ {} products available (maximum reached)</span>',
                count
            )
    product_count_info.short_description = 'Product Count'
    
    def product_preview(self, obj):
        """Display preview of products that will be shown"""
        products = obj.get_products()[:10]  # Show first 10
        
        if not products:
            return 'No products to display'
        
        html = '<div style="margin-top: 10px;">'
        html += f'<strong>First {len(products)} products:</strong><br><br>'
        
        for i, product in enumerate(products, 1):
            html += f'{i}. {product.name}'
            if hasattr(product, 'price') and product.price:
                html += f' - ${product.price}'
            html += '<br>'
        
        if obj.get_products().count() > 10:
            remaining = obj.get_products().count() - 10
            html += f'<br><em>... and {remaining} more product(s)</em>'
        
        html += '</div>'
        
        return format_html(html)
    product_preview.short_description = 'Product Preview'
    
    actions = ['activate_sections', 'deactivate_sections']
    
    def activate_sections(self, request, queryset):
        """Bulk action to activate selected sections"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} section(s) activated successfully.')
    activate_sections.short_description = 'Activate selected sections'
    
    def deactivate_sections(self, request, queryset):
        """Bulk action to deactivate selected sections"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} section(s) deactivated successfully.')
    deactivate_sections.short_description = 'Deactivate selected sections'
    
    def get_form(self, request, obj=None, **kwargs):
        """Customize form to show/hide fields based on section_type"""
        form = super().get_form(request, obj, **kwargs)
        
        # Add help text based on section type
        if obj:
            if obj.section_type == 'manual':
                form.base_fields['products'].help_text = 'Select the products to display in this section'
                form.base_fields['category'].help_text = 'Not used for manual selection'
            elif obj.section_type == 'category':
                form.base_fields['category'].help_text = 'Required: Select the category to display products from'
                form.base_fields['products'].help_text = 'Not used for category-based selection'
            else:
                form.base_fields['products'].help_text = 'Not used for automatic selection'
                form.base_fields['category'].help_text = 'Not used for automatic selection'
        
        return form
