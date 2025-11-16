from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from django.urls import reverse

# Create your models here.


class Category(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Category Name'
    )
    
    slug = models.SlugField(
        max_length=200,
        unique=True,
        db_index=True,
        help_text='URL-friendly version of name'
    )

    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='Parent Category',
        help_text='Leave empty for top-level category'
    )

    description = models.TextField(
        blank=True,
        help_text='Leave empty for top-level category'
    )

    image = models.ImageField(
        upload_to='categories/',
        blank=True,
        null=True,
        help_text='Category banner image'
    )

    is_active = models.BooleanField(
        default=True,
        help_text='Inactive categories are hidden from storefront'
    )
    
    display_order = models.IntegerField(
        default=0,
        help_text='Lower numbers appear first'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['display_order','name']

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('category_detail', args=[self.slug])
    

class Brand(models.Model):

    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Brand Name'
    )

    slug = models.SlugField(
        max_length=200,
        unique=True,
        db_index=True
    )

    description = models.TextField(
        blank=True,
        help_text='Brand description'
    )

    logo = models.ImageField(
        upload_to='brands/',
        blank=True,
        null=True,
        help_text='Brand logo'
    )

    website = models.URLField(
        blank=True,
        help_text='Brand website URL'
    )

    is_active = models.BooleanField(
        default=True,
        help_text='Inactive brands are hidden from storefront'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'brands'
        verbose_name = 'Brand'
        verbose_name_plural = 'Brands'
        ordering = ['name']

    def __str__(self):
        return self.name
    

class Product(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Product Title'
    )

    slug = models.SlugField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text='URL-friendly version of title'
    )


    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        related_name='products',
        null=True,
        blank=True,
        related_query_name='products'
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='products',
        null=True,
        blank=True,
        related_query_name='products'
    )

    description = models.TextField(
        blank=True,
        help_text='Product description'
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Product Price',
        help_text='Base/starting price (variants may differ)'
    )

    sale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        blank=True,
        null=True,
        verbose_name='Sale Price',
        help_text='Sale price (optional)'
    )

    stock = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text='Total stock across all variants (informational only)'
    )

    low_stock_threshold = models.IntegerField(
        default=5,
        help_text='Alert when stock falls below this number'
    )

    weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Weight in kg'
    )
    
    length = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Length in cm'
    )
    
    width = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Width in cm'
    )
    
    height = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Height in cm'
    )

    is_active = models.BooleanField(
        default=True,
        help_text='Inactive products are hidden from storefront'
    )

    meta_title = models.CharField(
        max_length=200,
        blank=True,
        help_text='SEO page title'
    )
    
    meta_description = models.CharField(
        max_length=300,
        blank=True,
        help_text='SEO meta description'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active', '-created_at']),
        ]

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('product-detail', kwargs={'slug': self.slug})

    def get_total_stock(self):
        """Calculate total stock across all variants."""
        total = self.variants.filter(is_active=True).aggregate(
            total_stock=models.Sum('stock')
        )['total_stock']
        return total if total else 0
    
    def is_in_stock(self):
        """Check if any variant is in stock."""
        return self.variants.filter(is_active=True, stock__gt=0).exists()
    
    def is_low_stock(self):
        """Check if total stock is below threshold."""
        total = self.get_total_stock()
        return 0 < total <= self.low_stock_threshold


class AttributeType(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text='E.g., Color, Size, Material'
    )

    slug = models.SlugField(
        unique=True,
        help_text='URL-friendly name'
    )

    display_order = models.IntegerField(
        default=0,
        help_text='Order in which attributes are shown'
    )

    class Meta:
        db_table = 'attribute_types'
        verbose_name = 'Attribute Type'
        verbose_name_plural = 'Attribute Types'
        ordering = ['display_order','name']

    def __str__(self):
        return self.name
    
    def save(self,*args,**kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args,**kwargs)


class AttributeValue(models.Model):
    attribute_type =models.ForeignKey(
        AttributeType,
        on_delete=models.CASCADE,
        related_name='values',
    )

    value = models.CharField(
        max_length=200,
        help_text='E.g., Red, Blue, Medium'
    )

    display_order = models.IntegerField(
        default=0,
        help_text='Order in which values are shown'
    )

    class Meta:
        db_table = 'attribute_values'
        verbose_name = 'Attribute Value'
        verbose_name_plural = 'Attribute Values'
        ordering = ['attribute_type','display_order','value']
        unique_together = ['attribute_type', 'value']

    def __str__(self):
        return f"{self.attribute_type.name}: {self.value}"


class ProductVariant(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='variants'
    )

    sku = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text='Unique identifier for the variant'
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text='Price of the variant'
    )

    sale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        null=True,
        blank=True,
        help_text='Sale price of the variant'
    )

    stock = models.PositiveIntegerField(
        default=0,
        help_text='Available stock for the variant'
    )

    weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Weight in kg'
    )

    is_active = models.BooleanField(
        default=True,
        help_text='Inactive variants are hidden from storefront'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'product_variants'
        verbose_name = 'Product Variant'
        verbose_name_plural = 'Product Variants'
        ordering = ['product', 'sku']

    def __str__(self):
        return f"{self.product.title} - {self.sku}"

    def get_base_price(self):
        """Get the base price (before discount)."""
        return self.price
    
    def get_sale_price(self):
        """Get the discounted price (if on sale)."""
        return self.sale_price
    
    def get_effective_price(self):
        if self.sale_price is not None:
            return self.sale_price
        return self.price

    def get_attributes_display(self):
        attrs = self.attributes.select_related('attribute_value__attribute_type').order_by(
            'attribute_value__attribute_type__display_order'
        )
        return ' / '.join([f"{av.attribute_value.value}" for av in attrs])

    def is_in_stock(self):
        return self.stock > 0
    
    def is_on_sale(self):
        return self.sale_price is not None


class VariantAttribute(models.Model):
    """
    Junction table linking variants to attribute values.
    E.g., Variant 1 = {Color: Red, Size: Medium}
    """
    product_variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name='attributes'
    )

    attribute_value = models.ForeignKey(
        AttributeValue,
        on_delete=models.CASCADE
    )

    class Meta:
        db_table = 'variant_attributes'
        verbose_name = 'Variant Attribute'
        verbose_name_plural = 'Variant Attributes'
        unique_together = ['product_variant', 'attribute_value']

    def __str__(self):
        return f"{self.product_variant} - {self.attribute_value}"


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )

    image = models.ImageField(
        upload_to='products/%Y/%m/',
        help_text='Product image'
    )

    alt_text = models.CharField(
        max_length=200,
        blank=True,
        help_text='Alternative text for accessibility'
    )

    position = models.IntegerField(
        default=0,
        help_text='Display order (0 = primary image)'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'product_images'
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'
        ordering = ['position']

    def __str__(self):
        return f"Image for {self.product.title} - Image {self.position}"

    def save(self,*args,**kwargs):
        if not self.alt_text:
            self.alt_text = f"{self.product.title} - Image {self.position + 1}"
        super().save(*args,**kwargs)