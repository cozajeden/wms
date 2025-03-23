from rest_framework.test import APIClient
from ..models import Company, CustomUser
from typing import Dict, Any, Generator
from django.utils import timezone
from rest_framework import status
from django.test import TestCase
from django.urls import reverse
from ..models import UserGroups
from functools import partial
from enum import StrEnum
from faker import Faker

faker = Faker()


def user_generator() -> Generator[Dict[str, Any], None, None]:
    """
    Generate random user data, including username, password, email and role.
    Role is always set to UserGroups.ADMIN
    """
    while True:
        yield {
            'username': faker.user_name(),
            'password': faker.password(),
            'email': faker.email(),
            'role': UserGroups.ADMIN.value,
        }

def company_generator() -> Generator[Dict[str, Any], None, None]:
    """Generate random company data, including name, domain and email."""
    while True:
        yield {
            'domain': faker.url(),
            'name': faker.company(),
            'email': faker.email()
        }


class API(StrEnum):
    login = reverse('users:login')
    register_user = reverse('users:register_user')
    refresh_token = reverse('users:refresh_token')
    register_company = reverse('users:register_company')

    @staticmethod
    def delete_user(user_pk: int) -> str:
        return reverse('users:delete_user', args=[user_pk])

class TestTokensAndUsers(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = APIClient()
        cls.random_user = user_generator()
        cls.random_company = company_generator()
        cls.default_company = next(cls.random_company)
        cls.default_company['is_active'] = True
        cls.default_company_obj = Company.objects.create(**cls.default_company)
        cls.superuser = next(cls.random_user)
        cls.superuser['is_superuser'] = True
        cls.superuser['is_staff'] = True
        cls.superuser['company_id'] = cls.default_company_obj.id
        cls.superuser_obj = CustomUser.objects.create_superuser(**cls.superuser)

    def tearDown(self):
        CustomUser.objects.exclude(username=self.superuser_obj.username).all().delete()
        Company.objects.exclude(id=1).delete()
        return super().tearDown()

    def login(self, user: Dict[str, Any]) -> str:
        """Login and return headers and refresh token dict"""
        response = self.client.post(API.login, {
            'username': user['username'],
            'password': user['password']
        })
        data = response.json()
        return {'Authorization': f'Bearer {data["access"]}'}, {'refresh': data['refresh']}

    def create_comapany(self, verified: bool = False) -> Company:
        """Create a new company"""
        company = next(self.random_company)
        response = self.client.post(API.register_company, company)
        assert response.status_code == status.HTTP_201_CREATED
        company = Company.objects.get(name=company['name'])
        company.is_active = verified
        company.save()
        return company

    def test_cant_create_user_without_auth(self):
        """Only authenticated users can create new users"""
        user = next(self.random_user)
        response = self.client.post(API.register_user, user)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert not CustomUser.objects.filter(**user).exists()

    def test_superuser_can_create_user_for_any_company(self):
        """Superuser can create users for any company"""
        headers, _ = self.login(self.superuser)
        for company in [self.create_comapany(), self.create_comapany(verified=True)]:
            user = next(self.random_user)
            user['company'] = company.id
            response = self.client.post(API.register_user, user, headers=headers)
            assert response.status_code == status.HTTP_201_CREATED
            assert CustomUser.objects.filter(username=user['username']).exists()

    def test_admin_can_create_user_for_their_company(self):
        """Admin can only create users for their company"""
        headers, _ = self.login(self.superuser)
        admin_user = next(self.random_user)
        admin_user['company'] = self.create_comapany(True).id
        response = self.client.post(API.register_user, admin_user, headers=headers)
        assert response.status_code == status.HTTP_201_CREATED
        assert CustomUser.objects.filter(username=admin_user['username']).exists()
        headers, _ = self.login(admin_user)
        user = next(self.random_user)
        user['company'] = self.default_company_obj.id
        response = self.client.post(API.register_user, user, headers=headers)
        assert response.status_code == status.HTTP_201_CREATED
        assert CustomUser.objects.get(username=user['username']).company_id == admin_user['company']

    def test_user_cant_login_unverified_company(self):
        """User can't login if the company is not verified"""
        headers, _ = self.login(self.superuser)
        for role, _ in CustomUser.ROLE_CHOICES:
            user = next(self.random_user)
            user['role'] = role
            user['company'] = self.create_comapany().id
            response = self.client.post(API.register_user, user, headers=headers)
            assert response.status_code == status.HTTP_201_CREATED
            assert CustomUser.objects.filter(username=user['username']).exists()
            response = self.client.post(API.login, user)
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_can_logged_user_refresh_token(self):
        """Logged user can refresh token"""
        _, refresh_token = self.login(self.superuser)
        response = self.client.post(API.refresh_token, refresh_token)
        assert response.status_code == status.HTTP_200_OK
        for role, _ in CustomUser.ROLE_CHOICES:
            user = next(self.random_user)
            user['role'] = role
            user['company'] = self.default_company_obj
            CustomUser.objects.create(**user)
            _, refresh_token = self.login(user)
            response = self.client.post(API.refresh_token, refresh_token)
            assert response.status_code == status.HTTP_200_OK

    def test_cant_login_when_expired(self):
        """User can't login if the company is expired"""
        headers, _ = self.login(self.superuser)
        for role, _ in CustomUser.ROLE_CHOICES:
            user = next(self.random_user)
            user['role'] = role
            user['company'] = self.create_comapany()
            user['company'].is_active = True
            user['company'].save()
            CustomUser.objects.create(**user)
            response = self.client.post(API.login, user, headers=headers)
            assert response.status_code == status.HTTP_200_OK
            user['company'].expiration_date = timezone.now() - timezone.timedelta(days=1)
            user['company'].save()
            response = self.client.post(API.login, user, headers=headers)
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_superuser_and_admin_can_delete_user(self):
            """
            Superuser and Admin can delete user.
            Other roles can't delete user.
            """
            headers, _ = self.login(self.superuser)
            login_user = next(self.random_user)
            login_user['company'] = self.default_company_obj
            login_user_obj = CustomUser.objects.create(**login_user)
            # Superuser can delete any user
            response = self.client.delete(API.delete_user(login_user_obj.id), headers=headers)
            assert response.status_code == status.HTTP_204_NO_CONTENT
            assert not CustomUser.objects.filter(username=login_user['username']).exists()
            login_user_obj = CustomUser.objects.create(**login_user)
            headers, _ = self.login(login_user)
            user = next(self.random_user)
            user['company'] = self.default_company_obj
            user_obj = CustomUser.objects.create(**user)
            # Admin can delete only users from their company
            response = self.client.delete(API.delete_user(user_obj.id), headers=headers)
            assert response.status_code == status.HTTP_204_NO_CONTENT
            assert not CustomUser.objects.filter(username=user['username']).exists()
            for role, _ in CustomUser.ROLE_CHOICES:
                if role == UserGroups.ADMIN.value: continue
                login_user_obj.role = role
                login_user_obj.save()
                headers, _ = self.login(login_user)
                user = next(self.random_user)
                user['company'] = self.default_company_obj
                user_obj = CustomUser.objects.create(**user)
                # Other roles can't delete user
                response = self.client.delete(API.delete_user(user_obj.id), headers=headers)
                assert response.status_code == status.HTTP_403_FORBIDDEN
                assert CustomUser.objects.filter(username=user['username']).exists()
