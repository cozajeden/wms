from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.auth.hashers import make_password
from django.core.mail import EmailMultiAlternatives
from django.db.models.functions import Now
from django.utils import timezone
from django.conf import settings
from django.db import models
from enum import StrEnum
from typing import Any, List, Callable
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator


class UserGroups(StrEnum):
    """Enumeration of available user roles in the system."""
    ADMIN = "Admin"
    WAREHOUSE_MANAGER = "Warehouse Manager"
    PICKER_PACKER = "Picker/Packer"


def default_expiration_date() -> timezone.datetime:
    """Calculate the default expiration date (30 days from now)."""
    return Now() + timezone.timedelta(days=30)


class CompanyManager(models.Manager):
    """Custom manager for Company model that handles email notifications."""
    
    def create(self, **kwargs: Any) -> 'Company':
        """
        Create a new company and send registration request email.
        
        Args:
            **kwargs: Company creation parameters
            
        Returns:
            Company: The created company instance
        """
        created_company = super().create(**kwargs)
        self._send_registration_email(created_company)
        return created_company
    
    def _send_registration_email(self, company: 'Company') -> None:
        """Send registration request email to admin."""
        subject = "REGISTRATION REQUEST"
        html_content = self._generate_html_content(company)
        text_content = self._generate_text_content(company)
        
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            to=[settings.EMAIL_ACCEPT_ADDRESS],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
    
    def _generate_html_content(self, company: 'Company') -> str:
        """Generate HTML content for registration email."""
        return f'''<p style="font-size:1.5rem;">Company registration request</p>
            <p>Company: {company.name}</p>
            <p>Domain: {company.domain}</p>
            <p>Email: {company.email}</p>
            <a href="{settings.EMAIL_ACCEPT_URL}?company_id={company.id}">Accept</a>'''
    
    def _generate_text_content(self, company: 'Company') -> str:
        """Generate plain text content for registration email."""
        return f'''Company registration request
            Company: {company.name}
            Domain: {company.domain}
            Email: {company.email}
            Accept: {settings.EMAIL_ACCEPT_URL}company_id={company.id}'''


class Company(models.Model):
    """Model representing a company in the system."""
    
    objects = CompanyManager()
    
    name = models.CharField(
        max_length=255,
        help_text="Company Name",
        verbose_name="Company Name",
        unique=True
    )
    domain = models.URLField(
        max_length=255,
        help_text="Company URL",
        verbose_name="Company URL",
        unique=True
    )
    email = models.EmailField(
        help_text="Contact Email",
        verbose_name="Contact Email",
        unique=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expiration_date = models.DateField(default=default_expiration_date)

    class Meta:
        db_table = "company"
        verbose_name = "Company"
        verbose_name_plural = "Companies"
        ordering = ['-created_at']

    def __str__(self) -> str:
        return self.name


class CustomUserManager(UserManager):
    """Custom user manager that handles password hashing."""
    
    def create(self, **kwargs: Any) -> 'CustomUser':
        """
        Create a new user with hashed password.
        
        Args:
            **kwargs: User creation parameters
            
        Returns:
            CustomUser: The created user instance
        """
        kwargs['password'] = make_password(kwargs['password'])
        return super().create(**kwargs)


class CustomUser(AbstractUser):
    """Custom user model extending Django's AbstractUser."""
    
    objects = CustomUserManager()
    
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        help_text="Associated company",
        verbose_name="Company"
    )
    ROLE_CHOICES = [(str(group), str(group)) for group in UserGroups]
    role = models.CharField(
        max_length=255,
        choices=ROLE_CHOICES,
        help_text="User's role in the system",
        verbose_name="Role"
    )
    REQUIRED_FIELDS = ['email', 'role', 'company_id']

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ['-date_joined']
