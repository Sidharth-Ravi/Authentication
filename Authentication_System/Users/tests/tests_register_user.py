import json
from django.test import TestCase, Client
from django.urls import reverse
from Users.models import CustomUser
from rest_framework import status

class TestRegisterUserView(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('register_user')
        self.user = CustomUser.objects.create(email="test+11@example.com")
        self.user.set_password("password123")
        self.user.save()


    def test_register_user_success(self):
        data = {
            "email": "test+10@example.com",
            "password": "password123"
        }
        response = self.client.post(self.url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("data", response.json())

    def test_register_user_email_exists(self):
        data = {
            "email": "test+11@example.com",
            "password": "password123"
        }
        response = self.client.post(self.url, json.dumps(data), content_type="application/json")
        print(response.json())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"error": "Email already exists."})

    def test_register_user_invalid_json(self):
        response = self.client.post(self.url, "invalid json", content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"error": "Invalid JSON format."})

    def test_register_user_missing_fields(self):
        data = {
            "email": "",
            "password": ""
        }
        response = self.client.post(self.url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"error": "Email and password are required."})

