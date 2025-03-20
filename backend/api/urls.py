from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views
from django.urls import path

app_name = 'api'

urlpatterns = [
    path('register/', views.RegisterUserView.as_view(), name='register'),
    path('register/company/', views.RegisterCompanyView.as_view(), name='register_company'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='refresh_token'),
]
