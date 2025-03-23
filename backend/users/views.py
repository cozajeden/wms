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
            return Response({'error': 'Company is not verified or not known'}, status=status.HTTP_401_UNAUTHORIZED)
        return super().post(request, *args, **kwargs)


class CreateUserView(generics.GenericAPIView):
    """Create a new user"""
    serializer_class = serializers.CustomUserSerializer

    def get_serializer_class(self):
        if self.request.user.is_superuser:
            # Superuser can create users for any company
            return serializers.RegisterUserSerializer
        return super().get_serializer_class()

    @swagger_auto_schema(responses={201: serializers.info_response, 400: serializers.error_response, 401: serializers.error_response},)
    def post(self, request: HttpRequest) -> Response:
        """       Create a new user.       <br>
        Superuser can create users for any company.<br>
        Admin can only create users for their company.
        """
        if request.user.is_superuser:
            serializer = serializers.RegisterUserSerializer(data=request.data)
        elif self.request.user.role != UserGroups.ADMIN.value:
            return Response({'error': 'Only admin can create users'}, status=status.HTTP_401_UNAUTHORIZED)
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


class CreateCompanyView(generics.GenericAPIView):
    serializer_class = serializers.RegisterCompanySerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(responses={201: serializers.info_response, 400: serializers.error_response},)
    def post(self, request: HttpRequest) -> Response:
        """
        Create a new company.<br>
        It will be inactive until verified.<br>
        This endpoint is public.
        """
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                'message': 'Added company successfully. ' +
                'After verifying, you will receive an email with login details. ' +
                'This usually takes few hours.',
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
