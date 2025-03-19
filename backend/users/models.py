from django.contrib.auth.models import AbstractUser
from .auth_decorators import UserGroups
from django.utils import timezone
from django.db import models


def default_expiration_date():
    return timezone.now() + timezone.timedelta(days=7)


class Company(models.Model):
    name = models.CharField(max_length=255)
    domain = models.CharField(max_length=255)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expiration_date = models.DateField(default=default_expiration_date)

    class Meta:
        db_table = "company"
        verbose_name = "Company"
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    ROLE_CHOICES = [(str(group), str(group)) for group in UserGroups]
    role = models.CharField(max_length=255, choices=ROLE_CHOICES)
    REQUIRED_FIELDS = ['email', 'role', 'company_id']
