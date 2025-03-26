from rest_framework_simplejwt.views import TokenRefreshView
from . import views
from django.urls import path

app_name = 'users'

urlpatterns = [
    path('user/create/', views.CreateUserView.as_view(), name='create_user'),
    path('company/create/', views.CreateCompanyView.as_view(), name='create_company'),
    path('company/accept/<int:pk>/', views.CreateCompanyView.as_view(), name='accept_company'),
    path('login/', views.OnlyVerifiedCompaniesTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='refresh_token'),
    path('user/delete/<int:pk>/', views.DeleteUserView.as_view(), name='delete_user'),
    path('user/update/<int:pk>/', views.UpdateUserView.as_view(), name='update_user_password'),
]
