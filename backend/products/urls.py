from . import views
from django.urls import path

app_name = 'products'

urlpatterns = [
    path('material/', views.MaterialViewSet.as_view(), name='material'),
]
