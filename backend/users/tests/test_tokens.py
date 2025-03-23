from rest_framework.test import APIClient
from ..models import Company, CustomUser
from typing import Dict, Any, Generator
from rest_framework import status
from django.test import TestCase
from django.urls import reverse
from ..models import UserGroups
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


class API:
    login = reverse('users:login')
    register_user = reverse('users:register_user')
    refresh_token = reverse('users:refresh_token')
    register_company = reverse('users:register_company')


class TestTokensAndUsers(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = APIClient()
        cls.random_user = user_generator()
        cls.random_company = company_generator()
        cls.default_company = Company.objects.get(id=1)
        cls.superuser = next(cls.random_user)
        cls.superuser['is_superuser'] = True
        cls.superuser['is_staff'] = True
        cls.superuser['company_id'] = cls.default_company.id
        cls.superuser_obj = CustomUser.objects.create_superuser(**cls.superuser)

    def tearDown(self):
        CustomUser.objects.all().delete()
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
        print(response.json())
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
        user['company'] = self.default_company.id
        response = self.client.post(API.register_user, user, headers=headers)
        assert response.status_code == status.HTTP_201_CREATED
        assert CustomUser.objects.get(username=user['username']).company_id == admin_user['company']

    def test_user_cant_login_unverified_company(self):
        """User can't login if the company is not verified"""
        headers, _ = self.login(self.superuser)
        for role in CustomUser.ROLE_CHOICES:
            user = next(self.random_user)
            user['role'] = role[0]
            user['company'] = self.create_comapany().id
            response = self.client.post(API.register_user, user, headers=headers)
            assert response.status_code == status.HTTP_201_CREATED
            assert CustomUser.objects.filter(username=user['username']).exists()
            try:
                headers, _ = self.login(user)
            except KeyError:
                pass
            else:
                assert False, "User with unverified company should not be able to login"

    def test_can_logged_user_refresh_token(self):
        """Logged user can refresh token"""
        _, refresh_token = self.login(self.superuser)
        response = self.client.post(API.refresh_token, refresh_token)
        assert response.status_code == status.HTTP_200_OK
        for role, _ in CustomUser.ROLE_CHOICES:
            user = next(self.random_user)
            user['role'] = role
            user['company'] = self.default_company
            CustomUser.objects.create(**user)
            _, refresh_token = self.login(user)
            response = self.client.post(API.refresh_token, refresh_token)
            assert response.status_code == status.HTTP_200_OK