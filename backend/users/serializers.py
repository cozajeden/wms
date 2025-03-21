from users.models import CustomUser, Company
from rest_framework import serializers


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('username', 'password', 'email', 'role')


class RegisterCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ('name', 'domain', 'email')


class RegisterUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('username', 'password', 'company', 'role', 'email')
