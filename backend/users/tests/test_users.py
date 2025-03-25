"""
Test suite for user authentication and authorization functionality.

This module contains tests for:
- User registration and authentication
- Company verification and expiration
- Role-based access control
- Token management
- User management operations (create, delete, update)
"""

from typing import Dict, Any, Generator, Tuple
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from faker import Faker
from ..models import Company, CustomUser, UserGroups

faker = Faker()


class API:
    """API endpoint constants for user-related operations."""
    
    login = reverse('users:login')
    register_user = reverse('users:register_user')
    refresh_token = reverse('users:refresh_token')
    register_company = reverse('users:register_company')

    @staticmethod
    def delete_user(user_pk: int) -> str:
        """Get URL for deleting a user."""
        return reverse('users:delete_user', args=[user_pk])

    @staticmethod
    def update_user(user_pk: int) -> str:
        """Get URL for updating a user."""
        return reverse('users:update_user', args=[user_pk])

    @staticmethod
    def update_user_password(user_pk: int) -> str:
        """Get URL for updating a user's password."""
        return reverse('users:update_user_password', args=[user_pk])


def user_generator() -> Generator[Dict[str, Any], None, None]:
    """
    Generate random user data for testing.
    
    Yields:
        Dict containing:
            - username: Random username
            - password: Random password
            - email: Random email
            - role: Always set to UserGroups.ADMIN
    """
    while True:
        yield {
            'username': faker.user_name(),
            'password': faker.password(),
            'email': faker.email(),
            'role': UserGroups.ADMIN.value,
        }


def company_generator() -> Generator[Dict[str, Any], None, None]:
    """
    Generate random company data for testing.
    
    Yields:
        Dict containing:
            - domain: Random URL
            - name: Random company name
            - email: Random email
    """
    while True:
        yield {
            'domain': faker.url(),
            'name': faker.company(),
            'email': faker.email()
        }


class TestTokensAndUsers(TestCase):
    """Test suite for user authentication and authorization functionality."""
    
    random_user_generator = user_generator()
    random_company_generator = company_generator()

    @classmethod
    def random_user(cls) -> Dict[str, Any]:
        return next(cls.random_user_generator)

    @classmethod
    def random_company(cls) -> Dict[str, Any]:
        return next(cls.random_company_generator)

    @classmethod
    def setUpClass(cls) -> None:
        """Set up test environment with default company and superuser."""
        super().setUpClass()
        cls.client = APIClient()
        
        # Create default company
        cls.default_company = cls.random_company()
        cls.default_company['is_active'] = True
        cls.default_company_obj = Company.objects.create(**cls.default_company)
        
        # Create superuser
        cls.superuser = cls.random_user()
        cls.superuser['is_superuser'] = True
        cls.superuser['is_staff'] = True
        cls.superuser['company_id'] = cls.default_company_obj.id
        cls.superuser_obj = CustomUser.objects.create_superuser(**cls.superuser)

    def tearDown(self) -> None:
        """Clean up test data after each test."""
        CustomUser.objects.exclude(username=self.superuser_obj.username).delete()
        Company.objects.exclude(id=1).delete()
        return super().tearDown()

    def login(self, user: Dict[str, Any]) -> Tuple[Dict[str, str], Dict[str, str]]:
        """
        Authenticate a user and return authentication tokens.
        
        Args:
            user: Dictionary containing username and password
            
        Returns:
            Tuple containing:
                - Headers dict with Bearer token
                - Refresh token dict
        """
        response = self.client.post(API.login, {
            'username': user['username'],
            'password': user['password']
        })
        data = response.json()
        return {'Authorization': f'Bearer {data["access"]}'}, {'refresh': data['refresh']}

    def create_company(self, verified: bool = False) -> Company:
        """
        Create a new company for testing.
        
        Args:
            verified: Whether the company should be marked as verified
            
        Returns:
            Created Company instance
        """
        company = self.random_company()
        response = self.client.post(API.register_company, company)
        assert response.status_code == status.HTTP_201_CREATED
        company = Company.objects.get(name=company['name'])
        company.is_active = verified
        company.save()
        return company

    def test_cant_create_user_without_auth(self) -> None:
        """
        Test that unauthenticated users cannot create new users.
        
        Verifies:
            - 401 status code is returned
            - User is not created in database
        """
        user = self.random_user()
        response = self.client.post(API.register_user, user)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert not CustomUser.objects.filter(**user).exists()

    def test_anonymous_user_cant_use_other_than_create_company(self) -> None:
        """
        Test that anonymous users can only create companies or login.
        
        Verifies:
            - 401 status code for user registration
            - 401 status code for token refresh
            - User is not created in database
        """
        user = self.random_user()
        response = self.client.post(API.register_user, user)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert not CustomUser.objects.filter(**user).exists()
        response = self.client.post(API.refresh_token, {'refresh': 'token'})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_superuser_can_create_user_for_any_company(self) -> None:
        """
        Test that superuser can create users for any company.
        
        Verifies:
            - 201 status code for user creation
            - User is created in database
            - Works for both verified and unverified companies
        """
        headers, _ = self.login(self.superuser)
        for company in [self.create_company(), self.create_company(verified=True)]:
            user = self.random_user()
            user['company'] = company.id
            response = self.client.post(API.register_user, user, headers=headers)
            assert response.status_code == status.HTTP_201_CREATED
            assert CustomUser.objects.filter(username=user['username']).exists()

    def test_admin_can_create_user_for_their_company(self) -> None:
        """
        Test that admin can only create users for their own company.
        
        Verifies:
            - 201 status code for user creation
            - User is created in database
            - Created user belongs to admin's company
        """
        headers, _ = self.login(self.superuser)
        admin_user = self.random_user()
        admin_user['company'] = self.create_company(True).id
        response = self.client.post(API.register_user, admin_user, headers=headers)
        assert response.status_code == status.HTTP_201_CREATED
        assert CustomUser.objects.filter(username=admin_user['username']).exists()
        
        headers, _ = self.login(admin_user)
        user = self.random_user()
        user['company'] = self.default_company_obj.id
        response = self.client.post(API.register_user, user, headers=headers)
        assert response.status_code == status.HTTP_201_CREATED
        assert CustomUser.objects.get(username=user['username']).company_id == admin_user['company']

    def test_non_admin_user_cant_create_user(self) -> None:
        """
        Test that non-admin users cannot create new users.
        
        Verifies:
            - 403 status code for user creation
            - User is not created in database
            - Tested for all non-admin roles
        """
        for role, _ in CustomUser.ROLE_CHOICES:
            if role == UserGroups.ADMIN.value:
                continue
                
            user = self.random_user()
            user['role'] = role
            user['company'] = self.default_company_obj
            CustomUser.objects.create(**user)
            
            headers, _ = self.login(user)
            new_user = self.random_user()
            new_user['company'] = self.default_company_obj
            response = self.client.post(API.register_user, new_user, headers=headers)
            assert response.status_code == status.HTTP_403_FORBIDDEN
            assert not CustomUser.objects.filter(username=new_user['username']).exists()

    def test_user_cant_login_unverified_company(self) -> None:
        """
        Test that users cannot login if their company is not verified.
        
        Verifies:
            - 201 status code for user creation
            - 401 status code for login attempt
            - Tested for all user roles
        """
        headers, _ = self.login(self.superuser)
        for role, _ in CustomUser.ROLE_CHOICES:
            user = self.random_user()
            user['role'] = role
            user['company'] = self.create_company().id
            response = self.client.post(API.register_user, user, headers=headers)
            assert response.status_code == status.HTTP_201_CREATED
            assert CustomUser.objects.filter(username=user['username']).exists()
            response = self.client.post(API.login, user)
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_can_logged_user_refresh_token(self) -> None:
        """
        Test that logged-in users can refresh their tokens.
        
        Verifies:
            - 200 status code for token refresh
            - Tested for superuser and all user roles
        """
        _, refresh_token = self.login(self.superuser)
        response = self.client.post(API.refresh_token, refresh_token)
        assert response.status_code == status.HTTP_200_OK
        
        for role, _ in CustomUser.ROLE_CHOICES:
            user = self.random_user()
            user['role'] = role
            user['company'] = self.default_company_obj
            CustomUser.objects.create(**user)
            _, refresh_token = self.login(user)
            response = self.client.post(API.refresh_token, refresh_token)
            assert response.status_code == status.HTTP_200_OK

    def test_cant_login_when_expired(self) -> None:
        """
        Test that users cannot login if their company has expired.
        
        Verifies:
            - 200 status code for initial login
            - 401 status code after company expiration
            - Tested for all user roles
        """
        headers, _ = self.login(self.superuser)
        for role, _ in CustomUser.ROLE_CHOICES:
            user = self.random_user()
            user['role'] = role
            user['company'] = self.create_company()
            user['company'].is_active = True
            user['company'].save()
            CustomUser.objects.create(**user)
            
            response = self.client.post(API.login, user, headers=headers)
            assert response.status_code == status.HTTP_200_OK
            
            user['company'].expiration_date = timezone.now() - timezone.timedelta(days=1)
            user['company'].save()
            response = self.client.post(API.login, user, headers=headers)
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_superuser_and_admin_can_delete_user(self) -> None:
        """
        Test user deletion permissions.
        
        Verifies:
            - Superuser can delete any user (204 status code)
            - Admin can delete users from their company (204 status code)
            - Other roles cannot delete users (403 status code)
            - Users are actually deleted from database
        """
        headers, _ = self.login(self.superuser)
        login_user = self.random_user()
        login_user['company'] = self.default_company_obj
        login_user_obj = CustomUser.objects.create(**login_user)
        
        # Test superuser deletion
        response = self.client.delete(API.delete_user(login_user_obj.id), headers=headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not CustomUser.objects.filter(username=login_user['username']).exists()
        
        # Test admin deletion
        login_user_obj = CustomUser.objects.create(**login_user)
        headers, _ = self.login(login_user)
        user = self.random_user()
        user['company'] = self.default_company_obj
        user_obj = CustomUser.objects.create(**user)
        response = self.client.delete(API.delete_user(user_obj.id), headers=headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not CustomUser.objects.filter(username=user['username']).exists()
        
        # Test other roles cannot delete
        for role, _ in CustomUser.ROLE_CHOICES:
            if role == UserGroups.ADMIN.value:
                continue
                
            login_user_obj.role = role
            login_user_obj.save()
            headers, _ = self.login(login_user)
            
            user = self.random_user()
            user['company'] = self.default_company_obj
            user_obj = CustomUser.objects.create(**user)
            response = self.client.delete(API.delete_user(user_obj.id), headers=headers)
            assert response.status_code == status.HTTP_403_FORBIDDEN
            assert CustomUser.objects.filter(username=user['username']).exists()
            
            response = self.client.delete(API.delete_user(login_user_obj.id), headers=headers)
            assert response.status_code == status.HTTP_403_FORBIDDEN
            assert CustomUser.objects.filter(username=login_user['username']).exists()

    def test_superuser_can_update_user_password(self) -> None:
        """
        Test that superuser can update any user's password.
        
        Verifies:
            - 200 status code for password update
            - User can login with new password
        """
        headers, _ = self.login(self.superuser)
        login_user = self.random_user()
        login_user['company'] = self.default_company_obj
        login_user_obj = CustomUser.objects.create(**login_user)
        
        login_user['password'] = faker.password()
        login_user.pop('company')
        response = self.client.patch(
            API.update_user_password(login_user_obj.id), 
            login_user, 
            headers=headers, 
            content_type='application/json'
        )
        assert response.status_code == status.HTTP_200_OK
        
        response = self.client.post(API.login, login_user)
        assert response.status_code == status.HTTP_200_OK

    def test_admin_can_update_user_password_within_the_same_company(self) -> None:
        """
        Test that admin can only update passwords for users in their company.
        
        Verifies:
            - 200 status code for same-company password update
            - 403 status code for different-company password update
            - User can login with new password when update is successful
            - User cannot login with new password when update fails
        """
        # Create admin user
        admin_user = self.random_user()
        admin_user['company'] = self.default_company_obj
        admin_user_obj = CustomUser.objects.create(**admin_user)
        headers, _ = self.login(admin_user)
        
        # Test same company password update
        user = self.random_user()
        user['company'] = self.default_company_obj
        user_obj = CustomUser.objects.create(**user)
        user.pop('company')
        user['password'] = faker.password()
        
        response = self.client.patch(
            API.update_user_password(user_obj.id), 
            user, 
            headers=headers, 
            content_type='application/json'
        )
        assert response.status_code == status.HTTP_200_OK
        response = self.client.post(API.login, user)
        assert response.status_code == status.HTTP_200_OK
        
        # Test different company password update
        company = self.random_company()
        company['is_active'] = True
        company_obj = Company.objects.create(**company)
        admin_user_obj.company = company_obj
        admin_user_obj.save()
        
        user['password'] = faker.password()
        headers, _ = self.login(admin_user)
        response = self.client.patch(
            API.update_user_password(user_obj.id), 
            user, 
            headers=headers, 
            content_type='application/json'
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        response = self.client.post(API.login, user)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
