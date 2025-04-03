from rest_framework_simplejwt.views import TokenObtainPairView
from django.db.models import Q, functions as db_functions
from rest_framework import generics, permissions, status
from users.models import UserGroups
from users.permissions import has_group_permission
from drf_yasg.utils import swagger_auto_schema
from rest_framework.request import Request
from rest_framework.response import Response
from . import serializers, models
from typing import Any
from django.db import transaction


class MaterialViewSet(generics.ListCreateAPIView):
    """View for managing materials."""
    queryset = models.Material.objects.all()
    serializer_class = serializers.MaterialSerializer
    permission_classes = [has_group_permission([UserGroups.ADMIN, UserGroups.WAREHOUSE_MANAGER])]

    @swagger_auto_schema(
        operation_description="Get all materials",
        responses={200: serializers.MaterialSerializer(many=True)},
    )
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new material",
        responses={201: serializers.MaterialSerializer},
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().post(request, *args, **kwargs)
