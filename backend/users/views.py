from rest_framework_simplejwt.views import TokenObtainPairView
from django.db.models import Q, functions as db_functions
from rest_framework import generics, permissions, status
from drf_yasg.utils import swagger_auto_schema
from users.models import CustomUser, UserGroups
from rest_framework.request import HttpRequest
from rest_framework.response import Response
from . import serializers


class OnlyVerifiedCompaniesTokenObtainPairView(TokenObtainPairView):
    @swagger_auto_schema(responses={401: serializers.error_response, 200: serializers.login_response},)
    def post(self, request: HttpRequest, *args, **kwargs) -> Response:
        """Only companies that are verified and not expired can login"""
        company_is_active = CustomUser.objects.filter(
            (Q(company__expiration_date__gte=db_functions.Now()) & Q(company__is_active=True)) | Q(is_superuser=True),
            username=request.POST.get('username'),
        ).exists()
        if not company_is_active:
            return Response({'error': 'Company is not verified or expired'}, status=status.HTTP_401_UNAUTHORIZED)
        return super().post(request, *args, **kwargs)


class CreateUserView(generics.GenericAPIView):
    """Create a new user"""
    serializer_class = serializers.CustomUserSerializer

    def get_serializer_class(self):
        if self.request.user.is_superuser:
            # Superuser can create users for any company
            return serializers.RegisterUserSerializer
        return super().get_serializer_class()

    @swagger_auto_schema(responses={201: serializers.info_response, 400: serializers.error_response, 401: serializers.error_response, 403: serializers.error_response},)
    def post(self, request: HttpRequest) -> Response:
        """       Create a new user.       <br>
        Superuser can create users for any company.<br>
        Admin can only create users for their company.
        """
        if request.user.is_superuser:
            serializer = serializers.RegisterUserSerializer(data=request.data)
        elif self.request.user.role != UserGroups.ADMIN.value:
            return Response({'error': 'Only admin can create users'}, status=status.HTTP_403_FORBIDDEN)
        else:
            # Admin can only create users for their company
            data = request.data.copy()
            data['company'] = request.user.company_id
            serializer = serializers.RegisterUserSerializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'message': 'User created'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class DeleteUserView(generics.DestroyAPIView):
    """Delete a user"""
    queryset = CustomUser.objects.all()
    serializer_class = serializers.CustomUserSerializer

    @swagger_auto_schema(responses={204: serializers.info_response, 401: serializers.error_response, 403: serializers.error_response},)
    def delete(self, request: HttpRequest, *args, **kwargs) -> Response:
        """Delete a user, only superuser and admin can delete"""
        user = self.get_object()
        if not request.user.is_superuser and not (user.company_id == request.user.company_id and request.user.role == UserGroups.ADMIN.value):
            return Response({'error': 'You are not allowed to delete this user'}, status=status.HTTP_403_FORBIDDEN)
        user.delete()
        return Response({'message': 'User deleted'}, status=status.HTTP_204_NO_CONTENT)


class UpdateUserView(generics.UpdateAPIView):
    """Update a user's password"""
    queryset = CustomUser.objects.all()
    serializer_class = serializers.UpdateUserPasswordSerializer
    http_method_names = ['patch']

    @swagger_auto_schema(responses={200: serializers.info_response, 400: serializers.error_response, 401: serializers.error_response, 403: serializers.error_response},)
    def patch(self, request: HttpRequest, *args, **kwargs) -> Response:
        """Update a user's password"""
        user = self.get_object()
        if not request.user.is_superuser and not (user.company_id == request.user.company_id and request.user.role == UserGroups.ADMIN.value) and user.id != request.user.id:
            return Response({'error': 'You are not allowed to update this user\'s password'}, status=status.HTTP_403_FORBIDDEN)
        user.set_password(request.data.get('password'))
        user.save()
        return Response({'message': 'User updated'}, status=status.HTTP_200_OK)


class CreateCompanyView(generics.CreateAPIView):
    serializer_class = serializers.RegisterCompanySerializer
    permission_classes = [permissions.AllowAny]
