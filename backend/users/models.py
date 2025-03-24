from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.auth.hashers import make_password
from django.core.mail import EmailMultiAlternatives
from django.db.models.functions import Now
from django.utils import timezone
from django.conf import settings
from django.db import models
from enum import StrEnum


class UserGroups(StrEnum):
    ADMIN = "Admin"
    WAREHOUSE_MANAGER = "Warehouse Manager"
    PICKER_PACKER = "Picker/Packer"


def default_expiration_date():
    return Now() + timezone.timedelta(days=30)


class CompanyManager(models.Manager):
    def create(self, **kwargs):
        """Send email with link to accept company registration"""
        created_company = super().create(**kwargs)
        subject = "REGISTRATION REQUEST"
        html_content = f'''<p style="font-size:1.5rem;">Company registration request</p>
            <p>Company: {created_company.name}</p>
            <p>Domain: {created_company.domain}</p>
            <p>Email: {created_company.email}</p>
            <a href="{settings.EMAIL_ACCEPT_URL}?company_id={created_company.id}">Accept</a>'''
        text_content = f'''Company registration request
            Company: {created_company.name}
            Domain: {created_company.domain}
            Email: {created_company.email}
            Accept: {settings.EMAIL_ACCEPT_URL}company_id={created_company.id}'''
        msg = EmailMultiAlternatives(
            subject, text_content,
            to=[settings.EMAIL_ACCEPT_ADDRESS],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return created_company
        


class Company(models.Model):
    objects = CompanyManager()
    name = models.CharField(max_length=255, help_text="Company Name", verbose_name="Company Name", unique=True)
    domain = models.URLField(max_length=255, help_text="Company URL", verbose_name="Company URL", unique=True)
    email = models.EmailField(help_text="Contact Email", verbose_name="Contact Email", unique=True)
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
