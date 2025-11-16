"""
API Views for authentication and user management
"""
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import login

from api.serializers import (
    UserSerializer,
    UserProfileSerializer,
    RegisterSerializer,
    LoginSerializer,
    ChangePasswordSerializer,
    AddressSerializer,
    ForgotPasswordSerializer,
    VerifyResetTokenSerializer,
    ResetPasswordSerializer,
    generate_jwt_token
)
from api.utils import (
    success_response,
    error_response,
    created_response,
    bad_request_response,
    StandardResponseMixin
)
from accounts.models import Address


class RegisterView(APIView):
    """
    POST /api/auth/register/
    Register a new user account
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = generate_jwt_token(user)
            
            return created_response(
                data={
                    'user': UserSerializer(user).data,
                    'token': token
                },
                message='User registered successfully'
            )
        
        return bad_request_response(
            message='Registration failed',
            errors=serializer.errors
        )


class LoginView(APIView):
    """
    POST /api/auth/login/
    Login with email and password
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            token = generate_jwt_token(user)
            
            return success_response(
                data={
                    'user': UserSerializer(user).data,
                    'token': token
                },
                message='Login successful'
            )
        
        return error_response(
            message='Invalid credentials',
            errors=serializer.errors,
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class ProfileView(APIView):
    """
    GET /api/auth/profile/ - Get current user profile with addresses
    PATCH /api/auth/profile/ - Update user profile
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get user profile with addresses"""
        serializer = UserProfileSerializer(request.user)
        return success_response(
            data=serializer.data,
            message='Profile retrieved successfully'
        )
    
    def patch(self, request):
        """Update user profile"""
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            # Return updated profile with addresses
            updated_profile = UserProfileSerializer(request.user)
            return success_response(
                data=updated_profile.data,
                message='Profile updated successfully'
            )
        
        return bad_request_response(
            message='Profile update failed',
            errors=serializer.errors
        )


class ChangePasswordView(APIView):
    """
    POST /api/auth/change-password/
    Change user password
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return success_response(
                message='Password changed successfully'
            )
        
        return bad_request_response(
            message='Password change failed',
            errors=serializer.errors
        )


class AddressListCreateView(StandardResponseMixin, generics.ListCreateAPIView):
    """
    GET /api/auth/addresses/ - List all user addresses
    POST /api/auth/addresses/ - Create new address
    """
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get addresses for current user"""
        return Address.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """Override create to return standardized response"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return created_response(
                data=serializer.data,
                message='Address created successfully'
            )
        return bad_request_response(
            message='Address creation failed',
            errors=serializer.errors
        )


class AddressDetailView(StandardResponseMixin, generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/auth/addresses/{id}/ - Get address detail
    PATCH /api/auth/addresses/{id}/ - Update address
    DELETE /api/auth/addresses/{id}/ - Delete address
    """
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get addresses for current user"""
        return Address.objects.filter(user=self.request.user)
    
    def update(self, request, *args, **kwargs):
        """Override update to return standardized response"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if serializer.is_valid():
            serializer.save()
            return success_response(
                data=serializer.data,
                message='Address updated successfully'
            )
        return bad_request_response(
            message='Address update failed',
            errors=serializer.errors
        )
    
    def destroy(self, request, *args, **kwargs):
        """Override destroy to return standardized response"""
        instance = self.get_object()
        instance.delete()
        return success_response(
            message='Address deleted successfully'
        )


class ForgotPasswordView(APIView):
    """
    POST /api/auth/forgot-password/
    Request password reset email
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                serializer.send_reset_email()
                return success_response(
                    message="If an account exists with this email, you will receive a password reset link shortly.",
                    status_code=status.HTTP_200_OK
                )
            except Exception as e:
                return error_response(
                    message="Failed to send reset email. Please try again.",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return bad_request_response(
            message="Invalid email address",
            errors=serializer.errors
        )


class VerifyResetTokenView(APIView):
    """
    POST /api/auth/verify-reset-token/
    Verify if reset token is valid
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = VerifyResetTokenSerializer(data=request.data)
        
        if serializer.is_valid():
            return success_response(
                message="Token is valid",
                data={
                    "valid": True,
                    "email": serializer.reset_token.user.email
                },
                status_code=status.HTTP_200_OK
            )
        
        return bad_request_response(
            message="Invalid or expired token",
            errors=serializer.errors
        )


class ResetPasswordView(APIView):
    """
    POST /api/auth/reset-password/
    Reset password using token
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            return success_response(
                message="Password reset successfully. You can now login with your new password.",
                data={
                    "email": user.email
                },
                status_code=status.HTTP_200_OK
            )
        
        return bad_request_response(
            message="Password reset failed",
            errors=serializer.errors
        )
