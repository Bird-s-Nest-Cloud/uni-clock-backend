from django.contrib import admin
from .models import (
    Category,Brand,Product,AttributeType,AttributeValue,ProductVariant,VariantAttribute,ProductImage
)

# Register your models here.


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'is_active', 'display_order', 'created_at']
    list_filter = ['is_active', 'parent', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['display_order', 'name']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'parent', 'description')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Settings', {
            'fields': ('is_active', 'display_order')
        }),
    )

    add_fieldsets = (
        ('Basic Information', {
            'fields': ('name','slug', 'parent', 'description')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Settings', {
            'fields': ('is_active', 'display_order')
        }),
    )

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return self.fieldsets
    

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'website', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Media', {
            'fields': ('logo',)
        }),
        ('Links', {
            'fields': ('website',)
        }),
        ('Settings', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        ('Basic Information', {
            'fields': ('name','slug', 'description')
        }),
        ('Media', {
            'fields': ('logo',)
        }),
        ('Links', {
            'fields': ('website',)
        }),
        ('Settings', {
            'fields': ('is_active',)
        }),
    )
    
    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return self.fieldsets
    

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'position']
    ordering = ['position']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'brand', 'is_active',
                    'get_total_stock', 'created_at']
    list_filter = ['category', 'brand', 'is_active', 'created_at']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ProductImageInline]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'category', 'brand', 'description')
        }),
        ('Pricing', {
            'fields': ('price', 'sale_price'),
            'description': 'Base prices.'
        }),
        ('Inventory', {
            'fields': ('stock', 'low_stock_threshold'),
            'description': 'Stock is informational. Actual stock tracked at variant level.'
        }),
        ('Physical Attributes', {
            'fields': ('weight', 'length', 'width', 'height'),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('is_active',)
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )

    add_fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'category', 'brand', 'description')
        }),
        ('Pricing', {
            'fields': ('price', 'sale_price'),
            'description': 'Base prices.'
        }),
        ('Inventory', {
            'fields': ('stock', 'low_stock_threshold'),
            'description': 'Stock is informational. Actual stock tracked at variant level.'
        }),
        ('Physical Attributes', {
            'fields': ('weight', 'length', 'width', 'height'),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('is_active',)
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
    )

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return self.fieldsets
    
    
    def get_total_stock(self, obj):
        """Display total stock across all variants."""
        return obj.get_total_stock()
    get_total_stock.short_description = 'Total Stock'



@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image', 'alt_text', 'position', 'created_at']
    list_filter = ['created_at', 'position']
    search_fields = ['product__title', 'alt_text']
    readonly_fields = ['created_at']
    ordering = ['product','position']

    fieldsets = (
        ('Product', {
            'fields': ('product',)
        }),
        ('Image Details', {
            'fields': ('image', 'alt_text', 'position')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(AttributeType)
class AttributeTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_order']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['display_order', 'name']
    readonly_fields = []
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug')
        }),
        ('Settings', {
            'fields': ('display_order',)
        }),
    )
    
    add_fieldsets = (
        ('Basic Information', {
            'fields': ('name','slug')
        }),
        ('Settings', {
            'fields': ('display_order',)
        }),
    )
    
    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return self.fieldsets
    

@admin.register(AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
    list_display = ['attribute_type', 'value', 'display_order']
    list_filter = ['attribute_type']
    search_fields = ['attribute_type__name', 'value']
    ordering = ['attribute_type', 'display_order', 'value']
    
    fieldsets = (
        ('Attribute', {
            'fields': ('attribute_type',)
        }),
        ('Value Details', {
            'fields': ('value', 'display_order')
        }),
    )
    
    add_fieldsets = (
        ('Attribute', {
            'fields': ('attribute_type',)
        }),
        ('Value Details', {
            'fields': ('value', 'display_order')
        }),
    )
    
    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return self.fieldsets
    

class VariantAttributeInline(admin.TabularInline):
    model = VariantAttribute
    extra = 1
    fields = ['attribute_value']
    verbose_name = 'Attribute'
    verbose_name_plural = 'Attributes'


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'sku', 'get_attributes_display', 'price', 'stock', 'is_active']
    list_filter = ['product', 'is_active']
    search_fields = ['product__title', 'sku']
    inlines = [VariantAttributeInline]
    ordering = ['product', 'sku']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Product & Variant', {
            'fields': ('product', 'sku', 'get_attributes_display')
        }),
        ('Pricing', {
            'fields': ('price', 'sale_price'),
            'description': 'Set variant-specific price and optional sale price.'
        }),
        ('Inventory', {
            'fields': ('stock',)
        }),
        ('Physical Attributes', {
            'fields': ('weight',),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    add_fieldsets = (
        ('Product & SKU', {
            'fields': ('product', 'sku')
        }),
        ('Pricing', {
            'fields': ('price', 'sale_price')
        }),
        ('Inventory', {
            'fields': ('stock',)
        }),
        ('Physical Attributes', {
            'fields': ('weight',),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    inlines = [VariantAttributeInline]

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return self.fieldsets
    
    def get_attributes_display(self, obj):
        return obj.get_attributes_display()
    get_attributes_display.short_description = 'Variations'

    

@admin.register(VariantAttribute)
class VariantAttributeAdmin(admin.ModelAdmin):
    list_display = ['product_variant', 'attribute_value']
    list_filter = ['product_variant__product', 'attribute_value__attribute_type']
    search_fields = ['product_variant__sku', 'attribute_value__value']
    
    fieldsets = (
        ('Variant', {
            'fields': ('product_variant',)
        }),
        ('Attribute', {
            'fields': ('attribute_value',)
        }),
    )