import json
from django.test import TestCase, Client
from django.urls import reverse
from Users.models import CustomUser
from rest_framework import status
from django.contrib.auth.hashers import make_password

class TestLoginView(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('login')
        self.user = CustomUser.objects.create(  # Use create_user instead of create
            email="test+11@example.com",
            password="password123"  # No need to hash manually, create_user does it
        )

    def test_login_success(self):
        data = {
            "email": "test+11@example.com",
            "password": "password123"
        }
        response = self.client.post(self.url, json.dumps(data), content_type="application/json")
        print(response.content)  # Add this line to print the response content
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.json())
        self.assertIn("refresh", response.json())

    def test_login_invalid_credentials(self):
        data = {
            "email": "test+11@example.com",
            "password": "wrongpassword"
        }
        response = self.client.post(self.url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.json())

    def test_login_invalid_json(self):
        response = self.client.post(self.url, "invalid json", content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"error": "Invalid JSON format."})

    def test_login_missing_fields(self):
        data = {
            "email": "",
            "password": ""
        }
        response = self.client.post(self.url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.json())
        self.assertIn("password", response.json())