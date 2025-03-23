from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.db import models
from enum import StrEnum


class UserGroups(StrEnum):
    ADMIN = "Admin"
    WAREHOUSE_MANAGER = "Warehouse Manager"
    PICKER_PACKER = "Picker/Packer"


def default_expiration_date():
    return timezone.now() + timezone.timedelta(days=7)


class Company(models.Model):
    name = models.CharField(max_length=255)
    domain = models.CharField(max_length=255)
    email = models.EmailField()
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expiration_date = models.DateField(default=default_expiration_date)

    class Meta:
        db_table = "company"
        verbose_name = "Company"
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.name


class CustomUserManager(UserManager):
    def create(self, **kwargs):
        kwargs['password'] = make_password(kwargs['password'])
        return super().create(**kwargs)


class CustomUser(AbstractUser):
    objects = CustomUserManager()
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    ROLE_CHOICES = [(str(group), str(group)) for group in UserGroups]
    role = models.CharField(max_length=255, choices=ROLE_CHOICES)
    REQUIRED_FIELDS = ['email', 'role', 'company_id']

