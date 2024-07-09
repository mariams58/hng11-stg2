# unitest module
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import User, Organization
from .serializers import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken

class UserTests(APITestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.create_org_url = reverse('organisation-create')

        self.user_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'password': 'securepassword',
            'phone': '1234567890'
        }

    def test_register_user(self):
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('accessToken', response.data['data'])
        self.assertIn('user', response.data['data'])

    def test_login_user(self):
        self.client.post(self.register_url, self.user_data, format='json')
        login_data = {
            'email': 'john.doe@example.com',
            'password': 'securepassword'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('accessToken', response.data['data'])
        self.assertIn('user', response.data['data'])

    def test_register_user_missing_fields(self):
        incomplete_data = self.user_data.copy()
        incomplete_data.pop('email')
        response = self.client.post(self.register_url, incomplete_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn('errors', response.data)

    def test_register_user_duplicate_email(self):
        self.client.post(self.register_url, self.user_data, format='json')
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn('errors', response.data)

    def test_token_generation(self):
        self.client.post(self.register_url, self.user_data, format='json')
        login_data = {
            'email': 'john.doe@example.com',
            'password': 'securepassword'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        token = response.data['data']['accessToken']
        decoded_token = RefreshToken(token)
        self.assertIn('user_id', decoded_token.payload)
        self.assertEqual(decoded_token.payload['user_id'], User.objects.get(email='john.doe@example.com').user_id)

    def test_organization_access_control(self):
        self.client.post(self.register_url, self.user_data, format='json')
        login_data = {
            'email': 'john.doe@example.com',
            'password': 'securepassword'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        token = response.data['data']['accessToken']
        org_data = {
            'name': 'New Org',
            'description': 'This is a new organization.'
        }
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = self.client.post(self.create_org_url, org_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        another_user_data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane.smith@example.com',
            'password': 'securepassword',
            'phone': '0987654321'
        }
        self.client.post(self.register_url, another_user_data, format='json')
        login_data = {
            'email': 'jane.smith@example.com',
            'password': 'securepassword'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        token = response.data['data']['accessToken']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        org_id = Organization.objects.get(name='John\'s Organization').org_id
        response = self.client.get(reverse('organization-detail', args=[org_id]))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)