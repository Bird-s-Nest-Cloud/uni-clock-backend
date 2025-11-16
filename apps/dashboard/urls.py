from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Authentication
    path('login/', views.admin_login, name='login'),
    path('logout/', views.admin_logout, name='logout'),
    
    # Dashboard
    path('', views.admin_dashboard, name='dashboard'),
    path('home/', views.admin_dashboard, name='dashboard_home'),
    
    # User Management
    path('users/', views.user_list, name='user_list'),
    path('users/add/', views.user_add, name='user_add'),
    path('users/<int:pk>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:pk>/delete/', views.user_delete, name='user_delete'),
    
    # Catalog Management
    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_add, name='category_add'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    
    # Brands
    path('brands/', views.brand_list, name='brand_list'),
    path('brands/add/', views.brand_add, name='brand_add'),
    path('brands/<int:pk>/edit/', views.brand_edit, name='brand_edit'),
    path('brands/<int:pk>/delete/', views.brand_delete, name='brand_delete'),
    
    # Products
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.product_add, name='product_add'),
    path('products/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    
    # Product Variants
    path('products/<int:product_id>/variants/', views.variant_list, name='variant_list'),
    path('products/<int:product_id>/variants/add/', views.variant_add, name='variant_add'),
    path('variants/<int:pk>/edit/', views.variant_edit, name='variant_edit'),
    path('variants/<int:pk>/delete/', views.variant_delete, name='variant_delete'),
    
    # Attributes
    path('attributes/', views.attribute_list, name='attribute_list'),
    path('attributes/add/', views.attribute_add, name='attribute_add'),
    path('attributes/<int:pk>/edit/', views.attribute_edit, name='attribute_edit'),
    path('attributes/<int:pk>/delete/', views.attribute_delete, name='attribute_delete'),
    
    # Attribute Values
    path('attributes/<int:attr_id>/values/', views.attribute_value_list, name='attribute_value_list'),
    path('attributes/<int:attr_id>/values/add/', views.attribute_value_add, name='attribute_value_add'),
    path('attribute-values/<int:pk>/edit/', views.attribute_value_edit, name='attribute_value_edit'),
    path('attribute-values/<int:pk>/delete/', views.attribute_value_delete, name='attribute_value_delete'),
    
    # Orders
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('orders/<int:pk>/status/', views.order_status_update, name='order_status_update'),
    
    # Banners
    path('banners/', views.banner_list, name='banner_list'),
    path('banners/add/', views.banner_add, name='banner_add'),
    path('banners/<int:pk>/edit/', views.banner_edit, name='banner_edit'),
    path('banners/<int:pk>/delete/', views.banner_delete, name='banner_delete'),
    path('banners/<int:pk>/toggle-status/', views.banner_toggle_status, name='banner_toggle_status'),
    
    # Featured Sections
    path('featured-sections/', views.featured_section_list, name='featured_section_list'),
    path('featured-sections/add/', views.featured_section_add, name='featured_section_add'),
    path('featured-sections/<int:pk>/edit/', views.featured_section_edit, name='featured_section_edit'),
    path('featured-sections/<int:pk>/delete/', views.featured_section_delete, name='featured_section_delete'),
    path('featured-sections/<int:pk>/toggle-status/', views.featured_section_toggle_status, name='featured_section_toggle_status'),
    path('featured-sections/<int:pk>/preview/', views.featured_section_preview, name='featured_section_preview'),
]