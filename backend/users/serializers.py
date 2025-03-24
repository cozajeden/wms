from users.models import CustomUser, Company
from rest_framework import serializers
from drf_yasg import openapi


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('username', 'password', 'email', 'role')


class UpdateUserPasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('password',)


class RegisterCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ('name', 'domain', 'email')


class RegisterUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('username', 'password', 'company', 'role', 'email')


class CommonResponseSerializer(serializers.Serializer):
    message = serializers.CharField(help_text='Information message')


class CommonErrorResponseSerializer(serializers.Serializer):
    error = serializers.CharField(help_text='Error message')


class LoginResponseSerializer(serializers.Serializer):
    access = serializers.CharField(help_text='Access token')
    refresh = serializers.CharField(help_text='Refresh token')


error_response = openapi.Response('Error message.', CommonErrorResponseSerializer)
info_response = openapi.Response('Information message.', CommonResponseSerializer)
login_response = openapi.Response('Login response.', LoginResponseSerializer)
