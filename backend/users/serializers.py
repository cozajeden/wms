from django.contrib.auth.hashers import make_password
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
        
    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)