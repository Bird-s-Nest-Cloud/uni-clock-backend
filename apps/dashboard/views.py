from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Sum, Max, Q
from django.http import JsonResponse

from accounts.models import User
from catalog.models import Category, Brand, Product, ProductVariant, AttributeType, AttributeValue
from orders.models import Order
from core.models import Banner, FeaturedSection

def admin_required(user):
    return user.is_authenticated and user.is_staff

def admin_login(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('dashboard:dashboard')
        else:
            messages.error(request, 'Access denied. Staff privileges required.')
            logout(request)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user and user.is_staff:
            login(request, user)
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('dashboard:dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'admin/auth/login.html')

@login_required
def admin_logout(request):
    logout(request)
    return redirect('dashboard:login')

@user_passes_test(admin_required)
def admin_dashboard(request):
    """Dashboard view with key metrics, top selling products, and low stock alerts"""
    from django.utils import timezone
    from catalog.models import Product, ProductVariant
    from orders.models import OrderItem
    
    # Get today's date
    today = timezone.now().date()
    
    # Statistics
    total_orders = Order.objects.count()
    total_customers = User.objects.filter(is_staff=False).count()
    todays_orders = Order.objects.filter(created_at__date=today).count()
    total_products = Product.objects.filter(is_active=True).count()
    
    # Top 5 selling products (based on order items quantity)
    top_selling_products = Product.objects.annotate(
        total_sold=Sum('variants__orderitem__quantity')
    ).filter(total_sold__gt=0).order_by('-total_sold')[:5]
    
    # Low stock products (variants with stock <= 10)
    low_stock_threshold = 10
    low_stock_products = ProductVariant.objects.select_related('product').filter(
        stock__lte=low_stock_threshold,
        is_active=True
    ).order_by('stock')[:10]
    
    context = {
        'total_orders': total_orders,
        'total_customers': total_customers,
        'todays_orders': todays_orders,
        'total_products': total_products,
        'top_selling_products': top_selling_products,
        'low_stock_products': low_stock_products,
        'low_stock_threshold': low_stock_threshold,
    }
    return render(request, 'admin/modules/dashboard/index.html', context)

# User Management Views
@user_passes_test(admin_required)
def user_list(request):
    """Display list of all users with search and filter"""
    users = User.objects.all().order_by('-date_joined')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        users = users.filter(
            Q(email__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    # Filter by staff status
    is_staff = request.GET.get('is_staff', '')
    if is_staff:
        users = users.filter(is_staff=is_staff == 'true')
    
    # Filter by active status
    is_active = request.GET.get('is_active', '')
    if is_active:
        users = users.filter(is_active=is_active == 'true')
    
    context = {
        'users': users,
        'search_query': search_query,
        'is_staff': is_staff,
        'is_active': is_active,
    }
    return render(request, 'admin/modules/users/list.html', context)

@user_passes_test(admin_required)
def user_add(request):
    """Add new user"""
    if request.method == 'POST':
        email = request.POST.get('email')
        name = request.POST.get('name')
        phone = request.POST.get('phone', '')
        password = request.POST.get('password')
        is_staff = request.POST.get('is_staff') == 'on'
        # Default to True if not explicitly set to off
        is_active = request.POST.get('is_active', 'on') == 'on'
        
        # Validation
        if not email or not name or not password:
            messages.error(request, 'Email, name, and password are required.')
            return render(request, 'admin/modules/users/add.html', {
                'email': email,
                'name': name,
                'phone': phone,
                'is_staff': is_staff,
                'is_active': is_active,
            })
        
        # Check if user exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'A user with this email already exists.')
            return render(request, 'admin/modules/users/add.html', {
                'email': email,
                'name': name,
                'phone': phone,
                'is_staff': is_staff,
                'is_active': is_active,
            })
        
        try:
            user = User.objects.create_user(
                email=email,
                password=password,
                name=name,
                phone=phone if phone else '',
            )
            user.is_staff = is_staff
            user.is_active = is_active
            user.save()
            
            messages.success(request, f'User "{user.name}" created successfully!')
            return redirect('dashboard:user_list')
        except Exception as e:
            messages.error(request, f'Error creating user: {str(e)}')
            return render(request, 'admin/modules/users/add.html', {
                'email': email,
                'name': name,
                'phone': phone,
                'is_staff': is_staff,
                'is_active': is_active,
            })
    
    return render(request, 'admin/modules/users/add.html')

@user_passes_test(admin_required)
def user_edit(request, pk):
    """Edit existing user"""
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        user.name = request.POST.get('name', user.name)
        user.email = request.POST.get('email', user.email)
        user.phone = request.POST.get('phone', '')
        user.is_staff = request.POST.get('is_staff') == 'on'
        user.is_active = request.POST.get('is_active') == 'on'
        
        # Update password if provided
        new_password = request.POST.get('new_password', '')
        if new_password:
            user.set_password(new_password)
        
        try:
            user.save()
            messages.success(request, f'User "{user.name}" updated successfully!')
            return redirect('dashboard:user_list')
        except Exception as e:
            messages.error(request, f'Error updating user: {str(e)}')
    
    context = {
        'user_obj': user,
        'title': f'Edit User: {user.name}',
    }
    return render(request, 'admin/modules/users/edit.html', context)

@user_passes_test(admin_required)
def user_delete(request, pk):
    """Delete user with confirmation"""
    user_obj = get_object_or_404(User, pk=pk)
    
    # Prevent deleting yourself
    if user_obj == request.user:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('dashboard:user_list')
    
    if request.method == 'POST':
        user_name = user_obj.name
        user_email = user_obj.email
        try:
            user_obj.delete()
            messages.success(request, f'User "{user_name}" ({user_email}) deleted successfully!')
            return redirect('dashboard:user_list')
        except Exception as e:
            messages.error(request, f'Error deleting user: {str(e)}')
            return redirect('dashboard:user_list')
    
    context = {
        'user_obj': user_obj,
    }
    return render(request, 'admin/modules/users/delete.html', context)

# Category Management Views
@user_passes_test(admin_required)
def category_list(request):
    """Display list of all categories with search and filter"""
    from catalog.forms import CategoryForm
    
    categories = Category.objects.select_related('parent').all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        categories = categories.filter(name__icontains=search_query)
    
    # Filter by active status
    is_active = request.GET.get('is_active', '')
    if is_active:
        categories = categories.filter(is_active=is_active == 'true')
    
    # Filter by parent
    parent_id = request.GET.get('parent', '')
    if parent_id:
        if parent_id == 'none':
            categories = categories.filter(parent__isnull=True)
        else:
            categories = categories.filter(parent_id=parent_id)
    
    context = {
        'categories': categories,
        'search_query': search_query,
        'is_active': is_active,
        'parent_id': parent_id,
        'all_categories': Category.objects.filter(parent__isnull=True),  # For parent filter
    }
    return render(request, 'admin/modules/categories/list.html', context)

@user_passes_test(admin_required)
def category_add(request):
    """Add new category"""
    from catalog.forms import CategoryForm
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.name}" created successfully!')
            return redirect('dashboard:category_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CategoryForm()
    
    context = {
        'form': form,
        'title': 'Add Category',
    }
    return render(request, 'admin/modules/categories/add.html', context)

@user_passes_test(admin_required)
def category_edit(request, pk):
    """Edit existing category"""
    from catalog.forms import CategoryForm
    
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.name}" updated successfully!')
            return redirect('dashboard:category_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CategoryForm(instance=category)
    
    context = {
        'form': form,
        'category': category,
        'title': f'Edit Category: {category.name}',
    }
    return render(request, 'admin/modules/categories/edit.html', context)

@user_passes_test(admin_required)
def category_delete(request, pk):
    """Delete category with confirmation"""
    category = get_object_or_404(Category, pk=pk)
    
    # Check if category has children
    has_children = category.children.exists()
    has_products = category.products.exists()
    
    if request.method == 'POST':
        category_name = category.name
        try:
            category.delete()
            messages.success(request, f'Category "{category_name}" deleted successfully!')
            return redirect('dashboard:category_list')
        except Exception as e:
            messages.error(request, f'Error deleting category: {str(e)}')
            return redirect('dashboard:category_list')
    
    context = {
        'category': category,
        'has_children': has_children,
        'has_products': has_products,
        'children_count': category.children.count(),
        'products_count': category.products.count(),
    }
    return render(request, 'admin/modules/categories/delete.html', context)

# Brand Management Views
@user_passes_test(admin_required)
def brand_list(request):
    """Display list of all brands with search and filter"""
    from catalog.forms import BrandForm
    
    brands = Brand.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        brands = brands.filter(name__icontains=search_query)
    
    # Filter by active status
    is_active = request.GET.get('is_active', '')
    if is_active:
        brands = brands.filter(is_active=is_active == 'true')
    
    context = {
        'brands': brands,
        'search_query': search_query,
        'is_active': is_active,
    }
    return render(request, 'admin/modules/brands/list.html', context)

@user_passes_test(admin_required)
def brand_add(request):
    """Add new brand"""
    from catalog.forms import BrandForm
    
    if request.method == 'POST':
        form = BrandForm(request.POST, request.FILES)
        if form.is_valid():
            brand = form.save()
            messages.success(request, f'Brand "{brand.name}" created successfully!')
            return redirect('dashboard:brand_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BrandForm()
    
    context = {
        'form': form,
        'title': 'Add Brand',
    }
    return render(request, 'admin/modules/brands/add.html', context)

@user_passes_test(admin_required)
def brand_edit(request, pk):
    """Edit existing brand"""
    from catalog.forms import BrandForm
    
    brand = get_object_or_404(Brand, pk=pk)
    
    if request.method == 'POST':
        form = BrandForm(request.POST, request.FILES, instance=brand)
        if form.is_valid():
            brand = form.save()
            messages.success(request, f'Brand "{brand.name}" updated successfully!')
            return redirect('dashboard:brand_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BrandForm(instance=brand)
    
    context = {
        'form': form,
        'brand': brand,
        'title': f'Edit Brand: {brand.name}',
    }
    return render(request, 'admin/modules/brands/edit.html', context)

@user_passes_test(admin_required)
def brand_delete(request, pk):
    """Delete brand with confirmation"""
    brand = get_object_or_404(Brand, pk=pk)
    
    # Check if brand has products
    has_products = brand.products.exists()
    
    if request.method == 'POST':
        brand_name = brand.name
        try:
            brand.delete()
            messages.success(request, f'Brand "{brand_name}" deleted successfully!')
            return redirect('dashboard:brand_list')
        except Exception as e:
            messages.error(request, f'Error deleting brand: {str(e)}')
            return redirect('dashboard:brand_list')
    
    context = {
        'brand': brand,
        'has_products': has_products,
        'products_count': brand.products.count(),
    }
    return render(request, 'admin/modules/brands/delete.html', context)

# Product Management Views
@user_passes_test(admin_required)
def product_list(request):
    """Display list of all products with search and filters"""
    from catalog.forms import ProductForm
    from catalog.models import ProductImage
    
    products = Product.objects.select_related('category', 'brand').prefetch_related('images').all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(title__icontains=search_query)
    
    # Filter by active status
    is_active = request.GET.get('is_active', '')
    if is_active:
        products = products.filter(is_active=is_active == 'true')
    
    # Filter by category
    category_id = request.GET.get('category', '')
    if category_id:
        products = products.filter(category_id=category_id)
    
    # Filter by brand
    brand_id = request.GET.get('brand', '')
    if brand_id:
        products = products.filter(brand_id=brand_id)
    
    context = {
        'products': products,
        'search_query': search_query,
        'is_active': is_active,
        'category_id': category_id,
        'brand_id': brand_id,
        'categories': Category.objects.all(),
        'brands': Brand.objects.all(),
    }
    return render(request, 'admin/modules/products/list.html', context)

@user_passes_test(admin_required)
def product_add(request):
    """Add new product with images"""
    from catalog.forms import ProductForm, ProductImageForm
    from catalog.models import ProductImage
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            
            # Handle multiple image uploads with positions
            images = request.FILES.getlist('images')
            positions = request.POST.getlist('image_positions')
            
            for idx, image in enumerate(images):
                # Use provided position or default to index
                position = int(positions[idx]) if idx < len(positions) else idx
                ProductImage.objects.create(
                    product=product,
                    image=image,
                    position=position,
                    alt_text=f"{product.title} - Image {position + 1}"
                )
            
            messages.success(request, f'Product "{product.title}" created successfully!')
            return redirect('dashboard:product_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProductForm()
    
    context = {
        'form': form,
        'title': 'Add Product',
        'categories': Category.objects.all(),
        'brands': Brand.objects.all(),
    }
    return render(request, 'admin/modules/products/add.html', context)

@user_passes_test(admin_required)
def product_edit(request, pk):
    """Edit existing product"""
    from catalog.forms import ProductForm, ProductImageForm
    from catalog.models import ProductImage
    
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            
            # Handle new image uploads with positions
            images = request.FILES.getlist('images')
            positions = request.POST.getlist('image_positions')
            
            if images:
                for idx, image in enumerate(images):
                    # Use provided position or calculate next available position
                    if idx < len(positions):
                        position = int(positions[idx])
                    else:
                        max_position = product.images.aggregate(max_pos=Max('position'))['max_pos'] or -1
                        position = max_position + 1
                    
                    ProductImage.objects.create(
                        product=product,
                        image=image,
                        position=position,
                        alt_text=f"{product.title} - Image {position + 1}"
                    )
            
            # Handle image deletions
            delete_images = request.POST.getlist('delete_images')
            if delete_images:
                ProductImage.objects.filter(id__in=delete_images).delete()
            
            messages.success(request, f'Product "{product.title}" updated successfully!')
            return redirect('dashboard:product_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProductForm(instance=product)
    
    context = {
        'form': form,
        'product': product,
        'title': f'Edit Product: {product.title}',
        'categories': Category.objects.all(),
        'brands': Brand.objects.all(),
        'product_images': product.images.all().order_by('position'),
    }
    return render(request, 'admin/modules/products/edit.html', context)

@user_passes_test(admin_required)
def product_delete(request, pk):
    """Delete product with confirmation"""
    product = get_object_or_404(Product, pk=pk)
    
    # Check related data
    has_variants = product.variants.exists()
    has_images = product.images.exists()
    
    if request.method == 'POST':
        product_title = product.title
        try:
            product.delete()
            messages.success(request, f'Product "{product_title}" deleted successfully!')
            return redirect('dashboard:product_list')
        except Exception as e:
            messages.error(request, f'Error deleting product: {str(e)}')
            return redirect('dashboard:product_list')
    
    context = {
        'product': product,
        'has_variants': has_variants,
        'has_images': has_images,
        'variants_count': product.variants.count(),
        'images_count': product.images.count(),
    }
    return render(request, 'admin/modules/products/delete.html', context)

# Product Variant Views
@user_passes_test(admin_required)
def variant_list(request, product_id):
    """Display list of all variants for a product"""
    product = get_object_or_404(Product, pk=product_id)
    variants = product.variants.select_related('product').prefetch_related(
        'attributes__attribute_value__attribute_type'
    ).all()
    
    # Search functionality
    search = request.GET.get('search', '')
    if search:
        variants = variants.filter(sku__icontains=search)
    
    # Filter by active status
    status = request.GET.get('status', '')
    if status == 'active':
        variants = variants.filter(is_active=True)
    elif status == 'inactive':
        variants = variants.filter(is_active=False)
    
    return render(request, 'admin/modules/variants/list.html', {
        'product': product,
        'variants': variants,
        'search': search,
        'status': status,
    })

@user_passes_test(admin_required)
def variant_add(request, product_id):
    """Add new variant to a product"""
    from catalog.forms import ProductVariantForm
    from catalog.models import AttributeType, AttributeValue, VariantAttribute
    
    product = get_object_or_404(Product, pk=product_id)
    
    if request.method == 'POST':
        form = ProductVariantForm(request.POST)
        if form.is_valid():
            variant = form.save(commit=False)
            variant.product = product
            variant.save()
            
            # Handle attribute assignments
            attribute_types = AttributeType.objects.all()
            for attr_type in attribute_types:
                attr_value_id = request.POST.get(f'attribute_{attr_type.id}')
                if attr_value_id:
                    try:
                        attr_value = AttributeValue.objects.get(id=attr_value_id, attribute_type=attr_type)
                        VariantAttribute.objects.create(
                            product_variant=variant,
                            attribute_value=attr_value
                        )
                    except AttributeValue.DoesNotExist:
                        pass
            
            messages.success(request, f'Variant "{variant.sku}" created successfully')
            return redirect('dashboard:variant_list', product_id=product.id)
    else:
        # Pre-fill with product defaults
        initial = {
            'price': product.price,
            'sale_price': product.sale_price,
            'weight': product.weight,
            'stock': 0,
        }
        form = ProductVariantForm(initial=initial)
    
    # Get all attribute types and their values for selection
    attribute_types = AttributeType.objects.prefetch_related('values').all()
    
    return render(request, 'admin/modules/variants/add.html', {
        'product': product,
        'form': form,
        'attribute_types': attribute_types,
    })

@user_passes_test(admin_required)
def variant_edit(request, pk):
    """Edit existing product variant"""
    from catalog.forms import ProductVariantForm
    from catalog.models import AttributeType, AttributeValue, VariantAttribute
    
    variant = get_object_or_404(ProductVariant.objects.select_related('product'), pk=pk)
    
    if request.method == 'POST':
        form = ProductVariantForm(request.POST, instance=variant)
        if form.is_valid():
            variant = form.save()
            
            # Update attribute assignments
            # First, remove all existing attributes
            variant.attributes.all().delete()
            
            # Then add new ones
            attribute_types = AttributeType.objects.all()
            for attr_type in attribute_types:
                attr_value_id = request.POST.get(f'attribute_{attr_type.id}')
                if attr_value_id:
                    try:
                        attr_value = AttributeValue.objects.get(id=attr_value_id, attribute_type=attr_type)
                        VariantAttribute.objects.create(
                            product_variant=variant,
                            attribute_value=attr_value
                        )
                    except AttributeValue.DoesNotExist:
                        pass
            
            messages.success(request, f'Variant "{variant.sku}" updated successfully')
            return redirect('dashboard:variant_list', product_id=variant.product.id)
    else:
        form = ProductVariantForm(instance=variant)
    
    # Get all attribute types and their values
    attribute_types = AttributeType.objects.prefetch_related('values').all()
    
    # Get current attribute selections
    current_attributes = {}
    for va in variant.attributes.select_related('attribute_value__attribute_type').all():
        current_attributes[va.attribute_value.attribute_type.id] = va.attribute_value.id
    
    return render(request, 'admin/modules/variants/edit.html', {
        'variant': variant,
        'product': variant.product,
        'form': form,
        'attribute_types': attribute_types,
        'current_attributes': current_attributes,
    })

@user_passes_test(admin_required)
def variant_delete(request, pk):
    """Delete product variant"""
    variant = get_object_or_404(
        ProductVariant.objects.select_related('product').prefetch_related('attributes'),
        pk=pk
    )
    product = variant.product
    
    if request.method == 'POST':
        sku = variant.sku
        variant.delete()
        messages.success(request, f'Variant "{sku}" deleted successfully')
        return redirect('dashboard:variant_list', product_id=product.id)
    
    return render(request, 'admin/modules/variants/delete.html', {
        'variant': variant,
        'product': product,
    })

# Attribute Management Views
@user_passes_test(admin_required)
def attribute_list(request):
    """Display list of all attribute types with search"""
    from catalog.forms import AttributeTypeForm
    
    attributes = AttributeType.objects.annotate(
        values_count=Count('values')
    ).all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        attributes = attributes.filter(name__icontains=search_query)
    
    context = {
        'attributes': attributes,
        'search_query': search_query,
    }
    return render(request, 'admin/modules/attributes/list.html', context)

@user_passes_test(admin_required)
def attribute_add(request):
    """Add new attribute type"""
    from catalog.forms import AttributeTypeForm
    
    if request.method == 'POST':
        form = AttributeTypeForm(request.POST)
        if form.is_valid():
            attribute = form.save()
            messages.success(request, f'Attribute "{attribute.name}" created successfully!')
            return redirect('dashboard:attribute_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AttributeTypeForm()
    
    context = {
        'form': form,
        'title': 'Add Attribute Type',
    }
    return render(request, 'admin/modules/attributes/add.html', context)

@user_passes_test(admin_required)
def attribute_edit(request, pk):
    """Edit existing attribute type"""
    from catalog.forms import AttributeTypeForm
    
    attribute = get_object_or_404(AttributeType, pk=pk)
    
    if request.method == 'POST':
        form = AttributeTypeForm(request.POST, instance=attribute)
        if form.is_valid():
            attribute = form.save()
            messages.success(request, f'Attribute "{attribute.name}" updated successfully!')
            return redirect('dashboard:attribute_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AttributeTypeForm(instance=attribute)
    
    context = {
        'form': form,
        'attribute': attribute,
        'title': f'Edit Attribute: {attribute.name}',
    }
    return render(request, 'admin/modules/attributes/edit.html', context)

@user_passes_test(admin_required)
def attribute_delete(request, pk):
    """Delete attribute type with confirmation"""
    attribute = get_object_or_404(AttributeType, pk=pk)
    
    # Count related data
    values_count = attribute.values.count()
    
    if request.method == 'POST':
        attribute_name = attribute.name
        try:
            attribute.delete()
            messages.success(request, f'Attribute "{attribute_name}" deleted successfully!')
            return redirect('dashboard:attribute_list')
        except Exception as e:
            messages.error(request, f'Error deleting attribute: {str(e)}')
            return redirect('dashboard:attribute_list')
    
    context = {
        'attribute': attribute,
        'values_count': values_count,
    }
    return render(request, 'admin/modules/attributes/delete.html', context)

# Attribute Value Management Views
@user_passes_test(admin_required)
def attribute_value_list(request, attr_id):
    """Display list of values for a specific attribute type"""
    from catalog.forms import AttributeValueForm
    
    attribute = get_object_or_404(AttributeType, pk=attr_id)
    values = attribute.values.all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        values = values.filter(value__icontains=search_query)
    
    context = {
        'attribute': attribute,
        'values': values,
        'search_query': search_query,
    }
    return render(request, 'admin/modules/attribute_values/list.html', context)

@user_passes_test(admin_required)
def attribute_value_add(request, attr_id):
    """Add new attribute value"""
    from catalog.forms import AttributeValueForm
    
    attribute = get_object_or_404(AttributeType, pk=attr_id)
    
    if request.method == 'POST':
        form = AttributeValueForm(request.POST, attribute_type=attribute)
        if form.is_valid():
            value = form.save(commit=False)
            value.attribute_type = attribute
            value.save()
            messages.success(request, f'Value "{value.value}" added successfully!')
            return redirect('dashboard:attribute_value_list', attr_id=attr_id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AttributeValueForm(attribute_type=attribute)
    
    context = {
        'form': form,
        'attribute': attribute,
        'title': f'Add Value to {attribute.name}',
    }
    return render(request, 'admin/modules/attribute_values/add.html', context)

@user_passes_test(admin_required)
def attribute_value_edit(request, pk):
    """Edit existing attribute value"""
    from catalog.forms import AttributeValueForm
    
    value = get_object_or_404(AttributeValue, pk=pk)
    
    if request.method == 'POST':
        form = AttributeValueForm(request.POST, instance=value)
        if form.is_valid():
            value = form.save()
            messages.success(request, f'Value "{value.value}" updated successfully!')
            return redirect('dashboard:attribute_value_list', attr_id=value.attribute_type.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AttributeValueForm(instance=value)
    
    context = {
        'form': form,
        'value': value,
        'title': f'Edit Value: {value.value}',
    }
    return render(request, 'admin/modules/attribute_values/edit.html', context)

@user_passes_test(admin_required)
def attribute_value_delete(request, pk):
    """Delete attribute value with confirmation"""
    value = get_object_or_404(AttributeValue, pk=pk)
    
    if request.method == 'POST':
        value_text = value.value
        attr_id = value.attribute_type.id
        try:
            value.delete()
            messages.success(request, f'Value "{value_text}" deleted successfully!')
            return redirect('dashboard:attribute_value_list', attr_id=attr_id)
        except Exception as e:
            messages.error(request, f'Error deleting value: {str(e)}')
            return redirect('dashboard:attribute_value_list', attr_id=attr_id)
    
    context = {
        'value': value,
    }
    return render(request, 'admin/modules/attribute_values/delete.html', context)

# Order Management Views
@user_passes_test(admin_required)
def order_list(request):
    """Display list of all orders with search and filter"""
    orders = Order.objects.select_related('user').prefetch_related('items').all().order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        orders = orders.filter(
            Q(order_number__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(user__name__icontains=search_query)
        )
    
    # Filter by status
    status = request.GET.get('status', '')
    if status:
        orders = orders.filter(status=status)
    
    # Filter by payment status
    payment_status = request.GET.get('payment_status', '')
    if payment_status:
        orders = orders.filter(payment_status=payment_status)
    
    context = {
        'orders': orders,
        'search_query': search_query,
        'status': status,
        'payment_status': payment_status,
        'status_choices': Order.STATUS_CHOICES,
        'payment_status_choices': Order.PAYMENT_STATUS_CHOICES,
    }
    return render(request, 'admin/modules/orders/list.html', context)

@user_passes_test(admin_required)
def order_detail(request, pk):
    """Display detailed order information"""
    order = get_object_or_404(
        Order.objects.select_related('user', 'billing_address', 'shipping_address')
        .prefetch_related('items__variant__product'),
        pk=pk
    )
    
    context = {
        'order': order,
        'status_choices': Order.STATUS_CHOICES,
        'payment_status_choices': Order.PAYMENT_STATUS_CHOICES,
    }
    return render(request, 'admin/modules/orders/detail.html', context)

@user_passes_test(admin_required)
def order_status_update(request, pk):
    """Update order status and payment status"""
    if request.method == 'POST':
        order = get_object_or_404(Order, pk=pk)
        
        # Update order status
        status = request.POST.get('status')
        if status and status in dict(Order.STATUS_CHOICES):
            order.status = status
            messages.success(request, f'Order status updated to "{dict(Order.STATUS_CHOICES)[status]}"')
        
        # Update payment status
        payment_status = request.POST.get('payment_status')
        if payment_status and payment_status in dict(Order.PAYMENT_STATUS_CHOICES):
            order.payment_status = payment_status
            messages.success(request, f'Payment status updated to "{dict(Order.PAYMENT_STATUS_CHOICES)[payment_status]}"')
        
        # Update notes
        notes = request.POST.get('notes', '')
        if notes:
            order.notes = notes
        
        order.save()
        return redirect('dashboard:order_detail', pk=pk)
    
    return redirect('dashboard:order_list')


# Banner Management Views
@user_passes_test(admin_required)
def banner_list(request):
    """Display list of all banners with search and filter"""
    banners = Banner.objects.select_related('link_product').all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        banners = banners.filter(title__icontains=search_query)
    
    # Filter by active status
    is_active = request.GET.get('is_active', '')
    if is_active:
        banners = banners.filter(is_active=is_active == 'true')
    
    context = {
        'banners': banners,
        'search_query': search_query,
        'is_active': is_active,
    }
    return render(request, 'admin/modules/banners/list.html', context)

@user_passes_test(admin_required)
def banner_add(request):
    """Add new banner"""
    if request.method == 'POST':
        from catalog.forms import BannerForm
        form = BannerForm(request.POST, request.FILES)
        if form.is_valid():
            banner = form.save()
            messages.success(request, f'Banner "{banner.title}" created successfully!')
            return redirect('dashboard:banner_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        from catalog.forms import BannerForm
        form = BannerForm()
    
    context = {
        'form': form,
        'title': 'Add Banner',
    }
    return render(request, 'admin/modules/banners/add.html', context)

@user_passes_test(admin_required)
def banner_edit(request, pk):
    """Edit existing banner"""
    banner = get_object_or_404(Banner, pk=pk)
    
    if request.method == 'POST':
        from catalog.forms import BannerForm
        form = BannerForm(request.POST, request.FILES, instance=banner)
        if form.is_valid():
            banner = form.save()
            messages.success(request, f'Banner "{banner.title}" updated successfully!')
            return redirect('dashboard:banner_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        from catalog.forms import BannerForm
        form = BannerForm(instance=banner)
    
    context = {
        'form': form,
        'banner': banner,
        'title': f'Edit Banner: {banner.title}',
    }
    return render(request, 'admin/modules/banners/edit.html', context)

@user_passes_test(admin_required)
def banner_delete(request, pk):
    """Delete banner with confirmation"""
    banner = get_object_or_404(Banner, pk=pk)
    
    if request.method == 'POST':
        banner_title = banner.title
        try:
            banner.delete()
            messages.success(request, f'Banner "{banner_title}" deleted successfully!')
            return redirect('dashboard:banner_list')
        except Exception as e:
            messages.error(request, f'Error deleting banner: {str(e)}')
            return redirect('dashboard:banner_list')
    
    context = {
        'banner': banner,
    }
    return render(request, 'admin/modules/banners/delete.html', context)

@user_passes_test(admin_required)
def banner_toggle_status(request, pk):
    """Toggle banner active status via AJAX"""
    if request.method == 'POST':
        banner = get_object_or_404(Banner, pk=pk)
        banner.is_active = not banner.is_active
        banner.save()
        return JsonResponse({
            'success': True,
            'is_active': banner.is_active,
            'message': f'Banner "{banner.title}" {"activated" if banner.is_active else "deactivated"}'
        })
    return JsonResponse({'success': False, 'message': 'Invalid request'})


# Featured Section Management Views
@user_passes_test(admin_required)
def featured_section_list(request):
    """Display list of all featured sections with search and filter"""
    sections = FeaturedSection.objects.prefetch_related('products').all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        sections = sections.filter(title__icontains=search_query)
    
    # Filter by active status
    is_active = request.GET.get('is_active', '')
    if is_active:
        sections = sections.filter(is_active=is_active == 'true')
    
    # Filter by section type
    section_type = request.GET.get('section_type', '')
    if section_type:
        sections = sections.filter(section_type=section_type)
    
    context = {
        'sections': sections,
        'search_query': search_query,
        'is_active': is_active,
        'section_type': section_type,
        'section_types': FeaturedSection.SECTION_TYPE_CHOICES,
    }
    return render(request, 'admin/modules/featured_sections/list.html', context)

@user_passes_test(admin_required)
def featured_section_add(request):
    """Add new featured section"""
    if request.method == 'POST':
        from catalog.forms import FeaturedSectionForm
        form = FeaturedSectionForm(request.POST)
        if form.is_valid():
            section = form.save()
            messages.success(request, f'Featured section "{section.title}" created successfully!')
            return redirect('dashboard:featured_section_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        from catalog.forms import FeaturedSectionForm
        form = FeaturedSectionForm()
    
    context = {
        'form': form,
        'title': 'Add Featured Section',
    }
    return render(request, 'admin/modules/featured_sections/add.html', context)

@user_passes_test(admin_required)
def featured_section_edit(request, pk):
    """Edit existing featured section"""
    section = get_object_or_404(FeaturedSection, pk=pk)
    
    if request.method == 'POST':
        from catalog.forms import FeaturedSectionForm
        form = FeaturedSectionForm(request.POST, instance=section)
        if form.is_valid():
            section = form.save()
            messages.success(request, f'Featured section "{section.title}" updated successfully!')
            return redirect('dashboard:featured_section_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        from catalog.forms import FeaturedSectionForm
        form = FeaturedSectionForm(instance=section)
    
    context = {
        'form': form,
        'section': section,
        'title': f'Edit Featured Section: {section.title}',
        'product_preview': section.get_products()[:10],  # Preview first 10 products
    }
    return render(request, 'admin/modules/featured_sections/edit.html', context)

@user_passes_test(admin_required)
def featured_section_delete(request, pk):
    """Delete featured section with confirmation"""
    section = get_object_or_404(FeaturedSection, pk=pk)
    
    if request.method == 'POST':
        section_title = section.title
        try:
            section.delete()
            messages.success(request, f'Featured section "{section_title}" deleted successfully!')
            return redirect('dashboard:featured_section_list')
        except Exception as e:
            messages.error(request, f'Error deleting section: {str(e)}')
            return redirect('dashboard:featured_section_list')
    
    context = {
        'section': section,
    }
    return render(request, 'admin/modules/featured_sections/delete.html', context)

@user_passes_test(admin_required)
def featured_section_toggle_status(request, pk):
    """Toggle featured section active status via AJAX"""
    if request.method == 'POST':
        section = get_object_or_404(FeaturedSection, pk=pk)
        section.is_active = not section.is_active
        section.save()
        return JsonResponse({
            'success': True,
            'is_active': section.is_active,
            'message': f'Section "{section.title}" {"activated" if section.is_active else "deactivated"}'
        })
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@user_passes_test(admin_required)
def featured_section_preview(request, pk):
    """Preview products for a featured section via AJAX"""
    section = get_object_or_404(FeaturedSection, pk=pk)
    products = section.get_products()
    
    products_data = [{
        'id': p.id,
        'name': p.name,
        'price': str(p.price) if hasattr(p, 'price') else None,
        'is_active': p.is_active,
    } for p in products]
    
    return JsonResponse({
        'success': True,
        'products': products_data,
        'count': len(products_data)
    })
