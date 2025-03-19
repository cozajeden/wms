from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from typing import List, Callable
from enum import StrEnum


class UserGroups(StrEnum):
    ADMIN = "Admin"
    WAREHOUSE_MANAGER = "Warehouse Manager"
    PICKER_PACKER = "Picker/Packer"
    SUPPLIER = "Supplier"
    OPERATOR = "Operator"


def check_permission_function(user_groups: List[UserGroups]) -> Callable:
    """
    Use this decorator to restrict access to a method view.
    
    Parameters
    ----------
    user_groups : List[UserGroups]
        List of user groups that are allowed to access the view.
    """
    return user_passes_test(
        lambda user:
            user.groups.filter(name__in=user_groups).exists()
            or user.is_superuser
    )

def check_permission_class(user_groups: List[UserGroups]) -> Callable:
    """
    Use this decorator to restrict access to a class view.
    
    Parameters
    ----------
    user_groups : List[UserGroups]
        List of user groups that are allowed to access the view.
    """
    return method_decorator(check_permission_function(user_groups), name="dispatch")
