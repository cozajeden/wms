from django.test import TestCase
from rest_framework.test import APIClient
from typing import Dict, Any, Generator
from rest_framework import status
from users.models import Company, CustomUser
from users.auth_decorators import UserGroups
from django.urls import reverse
import faker

def user_generator() -> Generator[Dict[str, Any], None, None]:
    """
    Generate random user data, including username, password, email and role.
    Role is always set to UserGroups.ADMIN
    """
    while True:
        yield {
            'username': faker.Faker().user_name(),
            'password': faker.Faker().password(),
            'email': faker.Faker().email(),
            'role': UserGroups.ADMIN.value
        }

def company_generator() -> Generator[Dict[str, Any], None, None]:
    """Generate random company data, including name, domain and email."""
    while True:
        yield {
            'name': faker.Faker().company(),
            'domain': faker.Faker().domain_name(),
            'email': faker.Faker().email()
        }


class TestTokensAndUsers(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.random_user = user_generator()
        cls.random_company = company_generator()
        cls.client = APIClient()
        cls.superuser = next(cls.random_user)
        # There always is a default company with id=1
        cls.superuser['company_id'] = 1
        cls.superuser['is_superuser'] = True
        cls.superuser['is_staff'] = True
        cls.superuser_obj = CustomUser.objects.create_superuser(**cls.superuser)
        cls.company_unverified = next(cls.random_company)
        cls.company_verified = next(cls.random_company)
        cls.company_verified['is_active'] = True
        cls.company_unverified_obj = Company.objects.create(**cls.company_unverified)
        cls.company_verified_obj = Company.objects.create(**cls.company_verified)
        cls.company_unverified_obj.save()
        cls.company_verified_obj.save()

    @classmethod
    def tearDownClass(cls):
        Company.objects.exclude(id=1).delete()
        super().tearDownClass()

    def tearDown(self):
        CustomUser.objects.all().delete()
        return super().tearDown()

    def login(self, user: Dict[str, Any]) -> str:
        """Login and return access and refresh tokens"""
        response = self.client.post(reverse('api:login'), {
            'username': user['username'],
            'password': user['password']
        })
        print(response.content)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        return data['access'], data['refresh']

    def test_cant_create_user_without_auth(self):
        """Only authenticated users can create new users"""
        user = next(self.random_user)
        response = self.client.post(reverse('api:register'), user)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert not CustomUser.objects.filter(**user).exists()

    def test_superuser_can_create_user_for_any_company(self):
        """Superuser can create users for any company"""
        token, _ = self.login(self.superuser)
        for company_id in [self.company_unverified_obj.id, self.company_verified_obj.id]:
            user = next(self.random_user)
            user['company'] = company_id
            response = self.client.post(reverse('api:register'), user, headers={'Authorization': f'Bearer {token}'})
            assert response.status_code == status.HTTP_201_CREATED
            assert CustomUser.objects.filter(username=user['username']).exists()

    def test_admin_can_create_user_for_their_company(self):
        """Admin can only create users for their company"""
        token, _ = self.login(self.superuser)
        admin_user = next(self.random_user)
        admin_user['company'] = self.company_unverified_obj.id
        admin_user['is_active'] = True
        response = self.client.post(reverse('api:register'), admin_user, headers={'Authorization': f'Bearer {token}'})
        user = CustomUser.objects.filter(username=admin_user['username']).first()
        print(user.__dict__)
        assert response.status_code == status.HTTP_201_CREATED
        assert CustomUser.objects.filter(username=admin_user['username']).exists()
        admin_token, _ = self.login(admin_user)
        user = next(self.random_user)
        response = self.client.post(reverse('api:register'), user, headers={'Authorization': f'Bearer {admin_token}'})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert not CustomUser.objects.filter(username=user['username']).exists()
        