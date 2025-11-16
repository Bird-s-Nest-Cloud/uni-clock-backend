from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from datetime import timedelta
import secrets

# Create your models here.

class UserManager(BaseUserManager):

    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        
        if not name:
            raise ValueError('Users must have a name')
        
        email = self.normalize_email(email)

        user = self.model(
            email=email,
            name=name,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self,email,name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']

    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return self.name
    

class Address(models.Model):

    ADDRESS_TYPE_CHOICES = [
        ('billing', 'Billing'),
        ('shipping', 'Shipping'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name='User')

    label = models.CharField(max_length=50, help_text='E.g., Home, Office, etc.', verbose_name='Label')

    address_type = models.CharField(max_length=20, choices=ADDRESS_TYPE_CHOICES, default='shipping', verbose_name='Address Type')

    street = models.CharField(max_length=255, verbose_name='Street Address')
    city = models.CharField(max_length=100, verbose_name='City')
    state = models.CharField(max_length=100, verbose_name='State')
    postal_code = models.CharField(max_length=20, verbose_name='Postal Code')
    country = models.CharField(max_length=100, default='Bangladesh', verbose_name='Country')
    phone = models.CharField(max_length=20, verbose_name='Phone Number')

    is_default_billing = models.BooleanField(default=False, verbose_name='Default Billing Address')
    is_default_shipping = models.BooleanField(default=False, verbose_name='Default Shipping Address')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'address_type', 'is_default_billing'],
                condition=models.Q(is_default_billing=True),
                name='unique_default_billing_per_user'
            ),
            models.UniqueConstraint(
                fields=['user', 'address_type', 'is_default_shipping'],
                condition=models.Q(is_default_shipping=True),
                name='unique_default_shipping_per_user'
            ),
        ]

    def __str__(self):
        return f"{self.label} - {self.user.email}"
    
    def save(self, *args, **kwargs):
        # If setting as default billing, unset other default billing addresses
        if self.is_default_billing:
            Address.objects.filter(
                user=self.user,
                address_type='billing',
                is_default_billing=True
            ).exclude(pk=self.pk).update(is_default_billing=False)
        
        # If setting as default shipping, unset other default shipping addresses
        if self.is_default_shipping:
            Address.objects.filter(
                user=self.user,
                address_type='shipping',
                is_default_shipping=True
            ).exclude(pk=self.pk).update(is_default_shipping=False)
        
        super().save(*args, **kwargs)
    
    def get_full_address(self):
        return f"{self.street}, {self.city}, {self.state}, {self.postal_code}, {self.country}"


class PasswordResetToken(models.Model):
    """Model to store password reset tokens"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'password_reset_tokens'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Reset token for {self.user.email}"
    
    @classmethod
    def generate_token(cls, user):
        """Generate a new password reset token"""
        # Invalidate all previous tokens for this user
        cls.objects.filter(user=user, used=False).update(used=True)
        
        # Generate new token
        token = secrets.token_urlsafe(32)
        expires_at = timezone.now() + timedelta(hours=1)  # 1 hour expiry
        
        return cls.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )
    
    def is_valid(self):
        """Check if token is valid"""
        return not self.used and timezone.now() < self.expires_at