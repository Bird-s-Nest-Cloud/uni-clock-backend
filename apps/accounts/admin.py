from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Address

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('email', 'name')
    ordering = ('-date_joined',)


    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name',)}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('email', 'name', 'password1', 'password2', 'is_staff', 'is_active'),
            },
        ),
    )

    readonly_fields = ['date_joined','last_login']


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'label', 'city', 'country', 'address_type', 'is_default_billing', 'is_default_shipping', 'created_at']
    list_filter = ['country', 'address_type', 'is_default_billing', 'is_default_shipping']
    search_fields = ['user__email', 'user__name', 'street', 'city']
    ordering = ['-created_at']
    
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Address Details', {'fields': ('label', 'address_type', 'street', 'city', 'state', 'postal_code', 'country', 'phone')}),
        ('Default Settings', {'fields': ('is_default_billing', 'is_default_shipping')}),
    )