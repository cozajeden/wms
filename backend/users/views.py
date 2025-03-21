from .serializers import RegisterUserSerializer, CustomUserSerializer, RegisterCompanySerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import generics, permissions, status
from rest_framework.request import HttpRequest
from rest_framework.response import Response
from users.models import CustomUser, Company
from .auth_decorators import UserGroups


class OnlyRegisteredCompanies(TokenObtainPairView):
    """Only companies that are verified can login"""
    def post(self, request: HttpRequest, *args, **kwargs) -> Response:
        print(request.POST.dict())
        company_is_active = CustomUser.objects.filter(
            username=request.POST.get('username'),
            company__is_active=True
        ).exists()
        if not company_is_active:
            return Response({'error': 'Company is not verified or not known'}, status=status.HTTP_401_UNAUTHORIZED)
        return super().post(request, *args, **kwargs)


class RegisterUserView(generics.GenericAPIView):
    """Create a new user"""
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Only superuser can create users for any company"""
        if self.request.user.is_superuser:
            return RegisterUserSerializer
        return super().get_serializer_class()

    def post(self, request: HttpRequest) -> Response:
        if request.user.is_superuser:
            serializer = RegisterUserSerializer(data=request.data)
        elif self.request.user.role != UserGroups.ADMIN.value:
            return Response({'error': 'Only admin can create users'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            # Admin can only create users for their company
            data = request.data.copy()
            data['company'] = request.user.company_id
            serializer = RegisterUserSerializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class RegisterCompanyView(generics.GenericAPIView):
    serializer_class = RegisterCompanySerializer

    def post(self, request: HttpRequest) -> Response:
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            company = serializer.save()
            return Response({
                'company': self.serializer_class(company).data,
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)