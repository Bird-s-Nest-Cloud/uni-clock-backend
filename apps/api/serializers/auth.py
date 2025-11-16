"""
API Serializers for authentication and user management
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.mail import send_mail
from django.conf import settings
from accounts.models import User, Address, PasswordResetToken
from rest_framework_simplejwt.tokens import AccessToken


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'phone', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class AddressSerializer(serializers.ModelSerializer):
    """Serializer for Address model"""
    
    class Meta:
        model = Address
        fields = [
            'id', 'label', 'street', 'city', 'state',
            'postal_code', 'country', 'phone', 'address_type',
            'is_default_billing', 'is_default_shipping', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def create(self, validated_data):
        """Create address for current user"""
        user = self.context['request'].user
        validated_data['user'] = user
        
        # If setting as default billing, unset other default billing addresses
        if validated_data.get('is_default_billing', False):
            Address.objects.filter(
                user=user,
                address_type__in=['billing'],
                is_default_billing=True
            ).update(is_default_billing=False)
        
        # If setting as default shipping, unset other default shipping addresses
        if validated_data.get('is_default_shipping', False):
            Address.objects.filter(
                user=user,
                address_type__in=['shipping'],
                is_default_shipping=True
            ).update(is_default_shipping=False)
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update address"""
        # If setting as default billing, unset other default billing addresses
        if validated_data.get('is_default_billing', False) and not instance.is_default_billing:
            Address.objects.filter(
                user=instance.user,
                address_type__in=['billing'],
                is_default_billing=True
            ).exclude(id=instance.id).update(is_default_billing=False)
        
        # If setting as default shipping, unset other default shipping addresses
        if validated_data.get('is_default_shipping', False) and not instance.is_default_shipping:
            Address.objects.filter(
                user=instance.user,
                address_type__in=['shipping'],
                is_default_shipping=True
            ).exclude(id=instance.id).update(is_default_shipping=False)
        
        return super().update(instance, validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
    """Enhanced serializer for User Profile with addresses"""
    addresses = AddressSerializer(many=True, read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'phone', 'date_joined', 'addresses']
        read_only_fields = ['id', 'date_joined']


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = ['email', 'name', 'password', 'phone']
        extra_kwargs = {
            'phone': {'required': False}
        }
    
    def validate_email(self, value):
        """Check if email already exists"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists.")
        return value.lower()
    
    def create(self, validated_data):
        """Create new user with hashed password"""
        user = User.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password'],
            phone=validated_data.get('phone', '')
        )
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        """Validate credentials and return user"""
        email = attrs.get('email', '').lower()
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password
            )
            
            if not user:
                raise serializers.ValidationError(
                    {'detail': 'Invalid email or password'},
                    code='authorization'
                )
            
            if not user.is_active:
                raise serializers.ValidationError(
                    {'detail': 'User account is disabled'},
                    code='authorization'
                )
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError(
                {'detail': 'Email and password are required'},
                code='authorization'
            )


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change"""
    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    
    def validate_old_password(self, value):
        """Check if old password is correct"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Incorrect password")
        return value
    
    def validate(self, attrs):
        """Ensure new password is different from old"""
        if attrs['old_password'] == attrs['new_password']:
            raise serializers.ValidationError(
                {'new_password': 'New password must be different from old password'}
            )
        return attrs
    
    def save(self):
        """Update user password"""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


def generate_jwt_token(user):
    """Generate JWT access token for user"""
    token = AccessToken.for_user(user)
    return str(token)


class ForgotPasswordSerializer(serializers.Serializer):
    """Serializer for forgot password request"""
    email = serializers.EmailField()
    
    def validate_email(self, value):
        """Check if user with email exists"""
        try:
            user = User.objects.get(email=value.lower())
            self.user = user
            return value
        except User.DoesNotExist:
            # Don't reveal if email exists or not (security best practice)
            # Still return success to prevent email enumeration
            return value
    
    def send_reset_email(self):
        """Send password reset email"""
        if not hasattr(self, 'user'):
            # Email doesn't exist, but don't reveal that
            return
        
        # Generate token
        reset_token = PasswordResetToken.generate_token(self.user)
        
        # Create reset link
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={reset_token.token}"
        
        # Email subject and message
        subject = "Password Reset Request - BikeShop"
        message = f"""
Hi {self.user.name},

You recently requested to reset your password for your BikeShop account.

Click the link below to reset your password:
{reset_link}

This link will expire in 1 hour.

If you didn't request a password reset, please ignore this email or contact support if you have concerns.

Thanks,
The BikeShop Team
        """
        
        html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
        .content {{ background-color: #f9f9f9; padding: 30px; margin-top: 0; border: 1px solid #ddd; }}
        .button {{ 
            display: inline-block; 
            padding: 12px 30px; 
            background-color: #4CAF50; 
            color: white !important; 
            text-decoration: none; 
            border-radius: 5px; 
            margin: 20px 0;
            font-weight: bold;
        }}
        .footer {{ margin-top: 20px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #666; }}
        .warning {{ background-color: #fff3cd; padding: 10px; border-left: 4px solid #ffc107; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 style="margin: 0;">🔐 Password Reset Request</h1>
        </div>
        <div class="content">
            <p>Hi <strong>{self.user.name}</strong>,</p>
            
            <p>You recently requested to reset your password for your BikeShop account.</p>
            
            <p style="text-align: center;">
                <a href="{reset_link}" class="button">Reset Password</a>
            </p>
            
            <p>Or copy and paste this link into your browser:</p>
            <p style="word-break: break-all; background-color: #fff; padding: 10px; border: 1px solid #ddd; border-radius: 3px;">
                <a href="{reset_link}">{reset_link}</a>
            </p>
            
            <div class="warning">
                <strong>⏱️ Important:</strong> This link will expire in 1 hour for security reasons.
            </div>
            
            <p>If you didn't request a password reset, please ignore this email or contact support if you have concerns.</p>
            
            <div class="footer">
                <p><strong>Thanks,</strong><br>The BikeShop Team</p>
                <p style="color: #999; font-size: 11px;">This is an automated email. Please do not reply to this message.</p>
            </div>
        </div>
    </div>
</body>
</html>
        """
        
        # Send email
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[self.user.email],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            print(f"Error sending email: {e}")
            raise serializers.ValidationError("Failed to send reset email. Please try again.")


class VerifyResetTokenSerializer(serializers.Serializer):
    """Serializer to verify reset token validity"""
    token = serializers.CharField()
    
    def validate_token(self, value):
        """Validate token exists and is valid"""
        try:
            reset_token = PasswordResetToken.objects.get(token=value)
            
            if not reset_token.is_valid():
                raise serializers.ValidationError("Token has expired or already been used")
            
            self.reset_token = reset_token
            return value
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError("Invalid token")


class ResetPasswordSerializer(serializers.Serializer):
    """Serializer for resetting password with token"""
    token = serializers.CharField()
    new_password = serializers.CharField(
        min_length=8, 
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    confirm_password = serializers.CharField(
        min_length=8, 
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, data):
        """Validate passwords match and token is valid"""
        # Check passwords match
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': "Passwords do not match"
            })
        
        # Validate token
        try:
            reset_token = PasswordResetToken.objects.get(token=data['token'])
            
            if not reset_token.is_valid():
                raise serializers.ValidationError({
                    'token': "Token has expired or already been used"
                })
            
            self.reset_token = reset_token
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError({
                'token': "Invalid token"
            })
        
        return data
    
    def save(self):
        """Reset user password"""
        user = self.reset_token.user
        user.set_password(self.validated_data['new_password'])
        user.save()
        
        # Mark token as used
        self.reset_token.used = True
        self.reset_token.save()
        
        # Invalidate all other tokens for this user
        PasswordResetToken.objects.filter(
            user=user,
            used=False
        ).update(used=True)
        
        return user
