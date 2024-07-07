from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import User, Organization

class UserTests(APITestCase):
    def test_register_user(self):
        url = reverse('register')
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "password": "password123",
            "phone": "1234567890"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('accessToken', response.data['data'])
        self.assertEqual(response.data['data']['user']['email'], data['email'])

    def test_login_user(self):
        url = reverse('login')
        user = User.objects.create_user(
            email="john.doe@example.com",
            first_name="John",
            last_name="Doe",
            password="password123"
        )
        data = {
            "email": "john.doe@example.com",
            "password": "password123"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)