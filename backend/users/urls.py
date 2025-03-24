from rest_framework_simplejwt.views import TokenRefreshView
from . import views
from django.urls import path

app_name = 'users'

urlpatterns = [
    path('register/', views.CreateUserView.as_view(), name='register_user'),
    path('register/company/', views.CreateCompanyView.as_view(), name='register_company'),
    path('login/', views.OnlyVerifiedCompaniesTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='refresh_token'),
    path('delete/<int:pk>/', views.DeleteUserView.as_view(), name='delete_user'),
    path('update/<int:pk>/', views.UpdateUserView.as_view(), name='update_user'),
]
