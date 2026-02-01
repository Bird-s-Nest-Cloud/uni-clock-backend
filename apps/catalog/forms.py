from django import forms
from django.utils.text import slugify
from .models import (
    Category, Brand, Product, ProductImage, 
    AttributeType, AttributeValue, ProductVariant, VariantAttribute
)
from core.models import Banner, FeaturedSection


class CategoryForm(forms.ModelForm):
    """Form for creating and updating categories"""
    
    class Meta:
        model = Category
        fields = ['name', 'slug', 'parent', 'description', 'image', 'is_active', 'display_order']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter category name',
                'required': True
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Auto-generated from name (optional)',
            }),
            'parent': forms.Select(attrs={
                'class': 'form-select',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter category description (optional)'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'display_order': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'min': '0'
            }),
        }
        help_texts = {
            'slug': 'Leave empty to auto-generate from name',
            'parent': 'Leave empty for top-level category',
            'description': 'Optional category description',
            'image': 'Upload category banner image (optional)',
            'is_active': 'Inactive categories are hidden from storefront',
            'display_order': 'Lower numbers appear first (default: 0)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Exclude self from parent choices when editing
        if self.instance.pk:
            self.fields['parent'].queryset = Category.objects.exclude(pk=self.instance.pk)
        
        # Make slug optional in form
        self.fields['slug'].required = False
        self.fields['parent'].required = False
        self.fields['description'].required = False
        self.fields['image'].required = False

    def clean_slug(self):
        """Auto-generate slug if not provided"""
        slug = self.cleaned_data.get('slug')
        name = self.cleaned_data.get('name')
        
        if not slug and name:
            slug = slugify(name)
        
        # Check for duplicate slugs (excluding current instance)
        qs = Category.objects.filter(slug=slug)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        
        if qs.exists():
            raise forms.ValidationError('A category with this slug already exists.')
        
        return slug

    def clean(self):
        """Validate parent relationship to prevent circular references"""
        cleaned_data = super().clean()
        parent = cleaned_data.get('parent')
        
        if parent and self.instance.pk:
            # Check if parent is not a descendant of self
            current = parent
            while current:
                if current.pk == self.instance.pk:
                    raise forms.ValidationError({
                        'parent': 'Cannot set a child category as parent (circular reference)'
                    })
                current = current.parent
        
        return cleaned_data


class BrandForm(forms.ModelForm):
    """Form for creating and updating brands"""
    
    class Meta:
        model = Brand
        fields = ['name', 'slug', 'description', 'logo', 'website', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter brand name',
                'required': True
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Auto-generated from name (optional)',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter brand description (optional)'
            }),
            'logo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False
        self.fields['description'].required = False
        self.fields['logo'].required = False
        self.fields['website'].required = False

    def clean_slug(self):
        """Auto-generate slug if not provided"""
        slug = self.cleaned_data.get('slug')
        name = self.cleaned_data.get('name')
        
        if not slug and name:
            slug = slugify(name)
        
        # Check for duplicate slugs (excluding current instance)
        qs = Brand.objects.filter(slug=slug)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        
        if qs.exists():
            raise forms.ValidationError('A brand with this slug already exists.')
        
        return slug


class AttributeTypeForm(forms.ModelForm):
    """Form for creating and updating attribute types"""
    
    class Meta:
        model = AttributeType
        fields = ['name', 'slug', 'display_order']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Color, Size, Material',
                'required': True
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Auto-generated from name (optional)',
            }),
            'display_order': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'min': '0'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False

    def clean_slug(self):
        """Auto-generate slug if not provided"""
        slug = self.cleaned_data.get('slug')
        name = self.cleaned_data.get('name')
        
        if not slug and name:
            slug = slugify(name)
        
        # Check for duplicate slugs (excluding current instance)
        qs = AttributeType.objects.filter(slug=slug)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        
        if qs.exists():
            raise forms.ValidationError('An attribute type with this slug already exists.')
        
        return slug


class AttributeValueForm(forms.ModelForm):
    """Form for creating and updating attribute values"""
    
    class Meta:
        model = AttributeValue
        fields = ['value', 'display_order']
        widgets = {
            'value': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Red, Blue, Medium, Large',
                'required': True
            }),
            'display_order': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'min': '0'
            }),
        }

    def __init__(self, *args, **kwargs):
        # Allow passing attribute_type for context (not used in form fields)
        self.attribute_type = kwargs.pop('attribute_type', None)
        super().__init__(*args, **kwargs)


class ProductForm(forms.ModelForm):
    """Form for creating and updating products"""
    
    class Meta:
        model = Product
        fields = [
            'title', 'slug', 'category', 'brand', 'description',
            'price', 'sale_price', 'stock', 'low_stock_threshold',
            'weight', 'length', 'width', 'height',
            'is_active', 'authentic', 'meta_title', 'meta_description'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter product title',
                'required': True
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Auto-generated from title (optional)',
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
            }),
            'brand': forms.Select(attrs={
                'class': 'form-select',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Enter product description'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
            'sale_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00 (optional)',
                'step': '0.01',
                'min': '0'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'min': '0'
            }),
            'low_stock_threshold': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '5',
                'min': '0'
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Weight in kg',
                'step': '0.01',
                'min': '0'
            }),
            'length': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Length in cm',
                'step': '0.01',
                'min': '0'
            }),
            'width': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Width in cm',
                'step': '0.01',
                'min': '0'
            }),
            'height': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Height in cm',
                'step': '0.01',
                'min': '0'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'authentic': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'meta_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'SEO page title (optional)',
            }),
            'meta_description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'SEO meta description (optional)',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False
        self.fields['category'].required = False
        self.fields['brand'].required = False
        self.fields['description'].required = False
        self.fields['sale_price'].required = False
        self.fields['weight'].required = False
        self.fields['length'].required = False
        self.fields['width'].required = False
        self.fields['height'].required = False
        self.fields['meta_title'].required = False
        self.fields['meta_description'].required = False

    def clean_slug(self):
        """Auto-generate slug if not provided"""
        slug = self.cleaned_data.get('slug')
        title = self.cleaned_data.get('title')
        
        if not slug and title:
            slug = slugify(title)
        
        # Check for duplicate slugs (excluding current instance)
        qs = Product.objects.filter(slug=slug)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        
        if qs.exists():
            raise forms.ValidationError('A product with this slug already exists.')
        
        return slug

    def clean(self):
        """Validate sale price is less than regular price"""
        cleaned_data = super().clean()
        price = cleaned_data.get('price')
        sale_price = cleaned_data.get('sale_price')
        
        if price and sale_price and sale_price >= price:
            raise forms.ValidationError({
                'sale_price': 'Sale price must be less than regular price.'
            })
        
        return cleaned_data


class ProductImageForm(forms.ModelForm):
    """Form for adding product images"""
    
    class Meta:
        model = ProductImage
        fields = ['image', 'alt_text', 'position']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'required': True
            }),
            'alt_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Alternative text for accessibility (optional)',
            }),
            'position': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0 (0 = primary image)',
                'min': '0'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['alt_text'].required = False


class ProductVariantForm(forms.ModelForm):
    """Form for creating and updating product variants"""
    
    class Meta:
        model = ProductVariant
        fields = ['sku', 'price', 'sale_price', 'stock', 'weight', 'is_active']
        widgets = {
            'sku': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., BIKE-001-RED-M',
                'required': True
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
                'required': True
            }),
            'sale_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00 (optional)',
                'step': '0.01',
                'min': '0'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'min': '0',
                'required': True
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Weight in kg (optional)',
                'step': '0.01',
                'min': '0'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def __init__(self, *args, **kwargs):
        # Allow passing product for context (not used in form fields)
        self.product = kwargs.pop('product', None)
        super().__init__(*args, **kwargs)
        
        self.fields['sale_price'].required = False
        self.fields['weight'].required = False

    def clean(self):
        """Validate sale price is less than regular price"""
        cleaned_data = super().clean()
        price = cleaned_data.get('price')
        sale_price = cleaned_data.get('sale_price')
        
        if price and sale_price and sale_price >= price:
            raise forms.ValidationError({
                'sale_price': 'Sale price must be less than regular price.'
            })
        
        return cleaned_data


class BannerForm(forms.ModelForm):
    """Form for creating and updating homepage banners"""
    
    class Meta:
        model = Banner
        fields = [
            'title', 'subtitle', 'image', 'mobile_image', 'link_product',
            'button_text', 'display_order', 'is_active', 'authentic', 'start_date', 'end_date'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter banner title',
                'required': True
            }),
            'subtitle': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter banner subtitle (optional)',
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'required': True
            }),
            'mobile_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'link_product': forms.Select(attrs={
                'class': 'form-select',
            }),
            'button_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Shop Now',
            }),
            'display_order': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'min': '0'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'authentic': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'start_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
            }),
            'end_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
            }),
        }
        help_texts = {
            'title': 'Main heading text for the banner',
            'subtitle': 'Optional descriptive text or tagline',
            'image': 'Main banner image for desktop view (recommended: 1920x600px)',
            'mobile_image': 'Optional mobile-optimized banner (recommended: 768x600px)',
            'link_product': 'Product to link to when banner is clicked (optional)',
            'button_text': 'Text displayed on the call-to-action button',
            'display_order': 'Lower numbers appear first (0 = highest priority)',
            'is_active': 'Inactive banners are not displayed on the site',
            'authentic': 'Check for authentic products, uncheck for replica products',
            'start_date': 'Optional: Banner will only display after this date/time',
            'end_date': 'Optional: Banner will stop displaying after this date/time',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make optional fields not required
        self.fields['subtitle'].required = False
        self.fields['mobile_image'].required = False
        self.fields['link_product'].required = False
        self.fields['start_date'].required = False
        self.fields['end_date'].required = False
        
        # Filter only active products for linking and add authentic/replica indicator
        self.fields['link_product'].queryset = Product.objects.filter(is_active=True).order_by('title')
        self.fields['link_product'].label_from_instance = lambda obj: f"{obj.title} [{'Authentic' if obj.authentic else 'Replica'}]"

    def clean(self):
        """Validate date range and product authenticity"""
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        authentic = cleaned_data.get('authentic')
        link_product = cleaned_data.get('link_product')
        
        if start_date and end_date and end_date <= start_date:
            raise forms.ValidationError({
                'end_date': 'End date must be after start date.'
            })
        
        # Validate that linked product matches banner's authentic setting
        if link_product and link_product.authentic != authentic:
            product_type = 'authentic' if link_product.authentic else 'replica'
            banner_type = 'authentic' if authentic else 'replica'
            raise forms.ValidationError({
                'link_product': f'Selected product is {product_type} but banner is set to {banner_type}. They must match.'
            })
        
        return cleaned_data


class FeaturedSectionForm(forms.ModelForm):
    """Form for creating and updating featured product sections"""
    
    class Meta:
        model = FeaturedSection
        fields = [
            'title', 'subtitle', 'section_type', 'products',
            'max_products', 'display_order', 'is_active'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter section title',
                'required': True
            }),
            'subtitle': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter section subtitle (optional)',
            }),
            'section_type': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_section_type',
                'required': True
            }),
            'products': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'id': 'id_products',
                'size': '10',
            }),
            'max_products': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '8',
                'min': '1',
                'max': '50'
            }),
            'display_order': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'min': '0'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        help_texts = {
            'title': 'Heading text for the product section',
            'subtitle': 'Optional descriptive text for the section',
            'section_type': 'Label/category for this section',
            'products': 'Select products to display in this section',
            'max_products': 'Maximum number of products to display (1-50)',
            'display_order': 'Lower numbers appear first on the homepage',
            'is_active': 'Inactive sections are not displayed on the homepage',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make optional fields not required
        self.fields['subtitle'].required = False
        self.fields['products'].required = True
        
        # Filter only active products and add authentic/replica indicator
        self.fields['products'].queryset = Product.objects.filter(is_active=True).order_by('title')
        self.fields['products'].label_from_instance = lambda obj: f"{obj.title} {'[Authentic]' if obj.authentic else '[Replica]'}"

    def clean(self):
        """Validate that at least one product is selected"""
        cleaned_data = super().clean()
        products = cleaned_data.get('products')
        
        # Validate products are required
        if not products:
            raise forms.ValidationError({
                'products': 'At least one product must be selected.'
            })
        
        return cleaned_data
