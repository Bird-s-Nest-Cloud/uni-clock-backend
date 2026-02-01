from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.urls import reverse
from catalog.models import Product, Category


# Create your models here.


class Banner(models.Model):
    """
    Hero or promotional banners for the homepage that can link to specific products.
    Supports scheduling and ordering for display control.
    """
    title = models.CharField(
        max_length=200,
        verbose_name='Banner Title',
        help_text='Main heading text for the banner'
    )
    
    subtitle = models.CharField(
        max_length=300,
        blank=True,
        verbose_name='Banner Subtitle',
        help_text='Optional descriptive text or tagline'
    )
    
    image = models.ImageField(
        upload_to='banners/%Y/%m/',
        verbose_name='Banner Image',
        help_text='Main banner image for desktop view'
    )
    
    mobile_image = models.ImageField(
        upload_to='banners/%Y/%m/mobile/',
        blank=True,
        null=True,
        verbose_name='Mobile Banner Image',
        help_text='Optional mobile-optimized banner image (uses main image if not provided)'
    )
    
    link_product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='banners',
        verbose_name='Linked Product',
        help_text='Product to link to when banner is clicked'
    )
    
    button_text = models.CharField(
        max_length=50,
        default='Shop Now',
        verbose_name='Button Text',
        help_text='Text displayed on the call-to-action button'
    )
    
    display_order = models.IntegerField(
        default=0,
        verbose_name='Display Order',
        help_text='Lower numbers appear first (0 = highest priority)'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Active Status',
        help_text='Inactive banners are not displayed on the site'
    )
    
    authentic = models.BooleanField(
        default=True,
        verbose_name='Authentic Product Banner',
        help_text='Set to True for authentic products, False for replica products'
    )
    
    start_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Start Date',
        help_text='Optional: Banner will only display after this date/time'
    )
    
    end_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='End Date',
        help_text='Optional: Banner will stop displaying after this date/time'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created At'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Updated At'
    )
    
    class Meta:
        db_table = 'banners'
        ordering = ['display_order', '-created_at']
        verbose_name = 'Banner'
        verbose_name_plural = 'Banners'
    
    def __str__(self):
        return self.title
    
    def get_link_url(self):
        """
        Returns the URL for the linked product if available.
        
        Returns:
            str: Product detail URL or None if no product is linked
        """
        if self.link_product:
            return self.link_product.get_absolute_url()
        return None
    
    def is_currently_active(self):
        """
        Checks if the banner is currently active based on active status and date range.
        
        Returns:
            bool: True if banner should be displayed, False otherwise
        """
        if not self.is_active:
            return False
        
        now = timezone.now()
        
        # Check start date
        if self.start_date and now < self.start_date:
            return False
        
        # Check end date
        if self.end_date and now > self.end_date:
            return False
        
        return True


class FeaturedSection(models.Model):
    """
    Configurable product sections for the homepage with manually selected products.
    """
    
    SECTION_TYPE_CHOICES = [
        ('new', 'New Arrivals'),
        ('featured', 'Featured Products'),
        ('sale', 'On Sale'),
        ('popular', 'Popular Products'),
        ('custom', 'Custom Section'),
    ]
    
    title = models.CharField(
        max_length=200,
        verbose_name='Section Title',
        help_text='Heading text for the product section'
    )
    
    subtitle = models.CharField(
        max_length=300,
        blank=True,
        verbose_name='Section Subtitle',
        help_text='Optional descriptive text for the section'
    )
    
    section_type = models.CharField(
        max_length=20,
        choices=SECTION_TYPE_CHOICES,
        default='custom',
        verbose_name='Section Type',
        help_text='Label/category for this section'
    )
    
    products = models.ManyToManyField(
        Product,
        blank=True,
        related_name='featured_in_sections',
        verbose_name='Products',
        help_text='Select products to display in this section'
    )
    
    max_products = models.IntegerField(
        default=8,
        validators=[
            MinValueValidator(1, message='Must display at least 1 product'),
            MaxValueValidator(50, message='Cannot display more than 50 products')
        ],
        verbose_name='Maximum Products',
        help_text='Maximum number of products to display (1-50)'
    )
    
    display_order = models.IntegerField(
        default=0,
        verbose_name='Display Order',
        help_text='Lower numbers appear first on the homepage'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Active Status',
        help_text='Inactive sections are not displayed on the homepage'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created At'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Updated At'
    )
    
    class Meta:
        db_table = 'featured_sections'
        ordering = ['display_order', '-created_at']
        verbose_name = 'Featured Section'
        verbose_name_plural = 'Featured Sections'
    
    def __str__(self):
        return self.title
    
    def get_products(self, watch_pref='authentic'):
        """
        Returns the manually selected products for this section.
        
        Args:
            watch_pref: 'authentic' or 'replica' to filter products
        
        Returns:
            QuerySet: Filtered Product queryset limited by max_products
        """
        # Determine if showing authentic or replica products
        is_authentic = watch_pref != 'replica'
        
        # Return manually selected products that are active and match the watch preference
        product_ids = self.products.filter(
            is_active=True,
            authentic=is_authentic
        ).values_list('id', flat=True)
        queryset = Product.objects.filter(id__in=product_ids)
        
        # Limit to max_products
        return queryset[:self.max_products]
