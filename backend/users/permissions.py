from rest_framework import permissions
from typing import List, Type, Any
from .models import UserGroups
from rest_framework.request import Request


def has_group_permission(required_groups: List[UserGroups]) -> Type[permissions.BasePermission]:
    """
    Factory function that returns a permission class for checking user groups.
    
    Args:
        required_groups: List of user groups that are allowed access
        
    Returns:
        A permission class that can be used in permission_classes
    """
    class HasGroupPermission(permissions.IsAuthenticated):
        """
        Permission class that checks if a user belongs to any of the required groups.
        """
        def has_permission(self, request: Request, view: Any) -> bool:
            if not super().has_permission(request, view):
                return False
            if request.user.is_superuser:
                return True
            return request.user.groups.filter(name__in=required_groups).exists()
    
    return HasGroupPermission

class IsCompanyAdmin(permissions.IsAuthenticated):
    """
    Permission class to check if user is an admin of their company.
    """
    def has_permission(self, request: Request, view: Any) -> bool:
        if not super().has_permission(request, view):
            return False
        if request.user.is_superuser:
            return True
        return request.user.role == UserGroups.ADMIN.value

class IsCompanyMember(permissions.IsAuthenticated):
    """
    Permission class to check if user belongs to the same company as the resource.
    """
    def has_object_permission(self, request: Request, view: Any, obj: Any) -> bool:
        if request.user.is_superuser:
            return True
        return request.user.company_id == getattr(obj, 'company_id', None) 