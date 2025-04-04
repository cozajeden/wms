from users.models import CustomUser, Company, UserGroups
from rest_framework import serializers
from drf_yasg import openapi
from django.db import transaction


class CustomUserSerializer(serializers.ModelSerializer):
    """Serializer for basic user information."""
    
    class Meta:
        model = CustomUser
        fields = ('username', 'password', 'email', 'role')
        extra_kwargs = {
            'password': {'write_only': True},
        }


class UpdateUserPasswordSerializer(serializers.ModelSerializer):
    """Serializer for updating user password."""
    
    class Meta:
        model = CustomUser
        fields = ('password',)
        extra_kwargs = {
            'password': {'write_only': True},
        }


class CreateCompanySerializer(serializers.ModelSerializer):
    """Serializer for company registration."""
    
    class Meta:
        model = Company
        fields = ('name', 'domain', 'email')


class CreateUserSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    class Meta:
        model = CustomUser
        fields = ('username', 'password', 'company', 'role', 'email')
        extra_kwargs = {
            'password': {'write_only': True},
        }


class CommonResponseSerializer(serializers.Serializer):
    """Base serializer for common API responses."""
    
    message = serializers.CharField(help_text='Information message')


class CommonErrorResponseSerializer(serializers.Serializer):
    """Base serializer for common API error responses."""
    
    error = serializers.CharField(help_text='Error message')


class LoginResponseSerializer(serializers.Serializer):
    """Serializer for login response containing tokens."""
    
    access = serializers.CharField(help_text='Access token')
    refresh = serializers.CharField(help_text='Refresh token')


class AcceptCompanySerializer(serializers.ModelSerializer):
    """Serializer for accepting company registration."""
    
    class Meta:
        model = Company
        fields = ('is_active',)



# Swagger documentation response schemas
error_response = openapi.Response(
    description='Error message.',
    schema=CommonErrorResponseSerializer
)
info_response = openapi.Response(
    description='Information message.',
    schema=CommonResponseSerializer
)
login_response = openapi.Response(
    description='Login response containing access and refresh tokens.',
    schema=LoginResponseSerializer
)


