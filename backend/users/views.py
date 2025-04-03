from rest_framework_simplejwt.views import TokenObtainPairView
from django.db.models import Q, functions as db_functions
from rest_framework import generics, permissions, status
from rest_framework.serializers import ModelSerializer
from drf_yasg.utils import swagger_auto_schema
from users.models import CustomUser, UserGroups
from rest_framework.request import Request
from rest_framework.response import Response
from . import serializers
from typing import Any
from django.db import transaction


class OnlyVerifiedCompaniesTokenObtainPairView(TokenObtainPairView):
    """Custom token view that only allows login for verified and non-expired companies."""
    
    @swagger_auto_schema(
        responses={
            401: serializers.error_response,
            200: serializers.login_response
        },
        operation_description="Authenticate user and return tokens if company is verified and not expired."
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Authenticate user and return tokens.
        
        Args:
            request: HTTP request object
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
            
        Returns:
            Response: JWT tokens if authentication successful
            
        Raises:
            Response: 401 error if company is not verified or expired
        """
        company_is_active = CustomUser.objects.filter(
            (Q(company__expiration_date__gte=db_functions.Now()) & Q(company__is_active=True)) | Q(is_superuser=True),
            username=request.data.get('username'),
        ).exists()
        
        if not company_is_active:
            return Response(
                {
                    'error': 'Company is not verified or expired',
                    'username': request.data.get('username'),
                    'password': request.data.get('password'),
                    },
                status=status.HTTP_401_UNAUTHORIZED
            )
        return super().post(request, *args, **kwargs)


class CreateUserView(generics.GenericAPIView):
    """View for creating new users with role-based permissions."""
    
    serializer_class = serializers.CustomUserSerializer

    def get_serializer_class(self) -> type[ModelSerializer]:
        """Get appropriate serializer based on user role."""
        if self.request.user.is_superuser:
            return serializers.CreateUserSerializer
        return super().get_serializer_class()

    @swagger_auto_schema(
        responses={
            201: serializers.info_response,
            400: serializers.error_response,
            401: serializers.error_response,
            403: serializers.error_response
        },
        operation_description="Create a new user. Superuser can create users for any company. Admin can only create users for their company."
    )
    def post(self, request: Request) -> Response:
        """
        Create a new user.
        
        Args:
            request: HTTP request object
            
        Returns:
            Response: Success message if user created successfully
            
        Raises:
            Response: 403 error if user lacks permission
            Response: 400 error if validation fails
        """
        if request.user.is_superuser:
            serializer = serializers.CreateUserSerializer(data=request.data)
        elif self.request.user.role != UserGroups.ADMIN.value:
            return Response(
                {'error': 'Only admin can create users'},
                status=status.HTTP_403_FORBIDDEN
            )
        else:
            data = request.data.copy()
            data['company'] = request.user.company_id
            serializer = serializers.CreateUserSerializer(data=data)
            
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                {'message': 'User created'},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class DeleteUserView(generics.DestroyAPIView):
    """View for deleting users with role-based permissions."""
    
    queryset = CustomUser.objects.all()
    serializer_class = serializers.CustomUserSerializer

    @swagger_auto_schema(
        responses={
            204: serializers.info_response,
            401: serializers.error_response,
            403: serializers.error_response
        },
        operation_description="Delete a user. Only superuser and admin can delete users."
    )
    def delete(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Delete a user.
        
        Args:
            request: HTTP request object
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
            
        Returns:
            Response: Success message if user deleted successfully
            
        Raises:
            Response: 403 error if user lacks permission
        """
        user = self.get_object()
        if not request.user.is_superuser and not (
            user.company_id == request.user.company_id and 
            request.user.role == UserGroups.ADMIN.value
        ):
            return Response(
                {'error': 'You are not allowed to delete this user'},
                status=status.HTTP_403_FORBIDDEN
            )
        user.delete()
        return Response(
            {'message': 'User deleted'},
            status=status.HTTP_204_NO_CONTENT
        )


class UpdateUserView(generics.UpdateAPIView):
    """View for updating user passwords with role-based permissions."""
    
    queryset = CustomUser.objects.all()
    serializer_class = serializers.UpdateUserPasswordSerializer
    http_method_names = ['patch']

    @swagger_auto_schema(
        responses={
            200: serializers.info_response,
            400: serializers.error_response,
            401: serializers.error_response,
            403: serializers.error_response
        },
        operation_description="Update a user's password. Only superuser, admin, and the user themselves can update passwords."
    )
    def patch(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Update a user's password.
        
        Args:
            request: HTTP request object
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
            
        Returns:
            Response: Success message if password updated successfully
            
        Raises:
            Response: 403 error if user lacks permission
        """
        user = self.get_object()
        if not request.user.is_superuser and not (
            user.company_id == request.user.company_id and 
            request.user.role == UserGroups.ADMIN.value
        ) and user.id != request.user.id:
            return Response(
                {'error': 'You are not allowed to update this user\'s password'},
                status=status.HTTP_403_FORBIDDEN
            )
        user.set_password(request.data.get('password'))
        user.save()
        return Response(
            {'message': 'User updated'},
            status=status.HTTP_200_OK
        )


class CreateCompanyView(generics.GenericAPIView):
    """View for creating new companies with admin user."""
    
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        responses={
            201: serializers.info_response,
            400: serializers.error_response
        },
        operation_description="Create a new company and its admin user."
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Create a new company and its admin user in an atomic transaction.
        
        Args:
            request: HTTP request object containing company and user data
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
            
        Returns:
            Response: Success message if company and user created successfully
        """
        with transaction.atomic():
            company = serializers.CreateCompanySerializer(data=request.data)
            company.is_valid(raise_exception=True)
            company.save()
            
            data = request.data.copy()
            data['company'] = company.instance.pk
            data['role'] = UserGroups.ADMIN.value
            
            user = serializers.CreateUserSerializer(data=data)
            user.is_valid(raise_exception=True)
            user.save()
        
        return Response(
            {'message': 'Company and admin user created successfully'},
            status=status.HTTP_201_CREATED
        )


class AcceptCompanyView(generics.UpdateAPIView):
    """View for accepting companies."""
    
    queryset = CustomUser.objects.all()
    serializer_class = serializers.AcceptCompanySerializer

    @swagger_auto_schema(
        responses={
            200: serializers.info_response,
            400: serializers.error_response,
            401: serializers.error_response,
            403: serializers.error_response
        },
        operation_description="Accept a company. Only superuser can accept companies."
    )
    def patch(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Accept a company.
        
        Args:
            request: HTTP request object
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
            
        Returns:
            Response: Success message if company accepted successfully
            
        Raises:
            Response: 403 error if user lacks permission
        """
        if not request.user.is_superuser:
            return Response(
                {'error': 'You are not allowed to accept companies'},
                status=status.HTTP_403_FORBIDDEN
            )
        company = self.get_object().company
        company.is_active = True
        company.save()
        return Response(
            {'message': 'Company accepted'},
            status=status.HTTP_200_OK
        )