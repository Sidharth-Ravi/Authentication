import json
from django.test import TestCase, Client
from django.urls import reverse
from Users.models import CustomUser
from rest_framework import status
from django.utils import timezone
from datetime import timedelta

class TestVerifyOtpView(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('verify_otp')
        self.user = CustomUser.objects.create(
            email="test@example.com",
            otp="123456",
            otp_expiration=timezone.now() + timedelta(minutes=30)
        )

    def test_verify_otp_success(self):
        data = {
            "email": "test@example.com",
            "otp": "123456"
        }
        response = self.client.post(self.url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"message": "OTP verified successfully. Account activated."})

    def test_verify_otp_user_not_found(self):
        data = {
            "email": "nonexistent@example.com",
            "otp": "123456"
        }
        response = self.client.post(self.url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json(), {"error": "User not found."})

    def test_verify_otp_invalid_otp(self):
        data = {
            "email": "test@example.com",
            "otp": "000000"
        }
        response = self.client.post(self.url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"error": "Invalid or expired OTP."})

    def test_verify_otp_invalid_json(self):
        response = self.client.post(self.url, "invalid json", content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"error": "Invalid JSON data."})

    def test_verify_otp_missing_fields(self):
        data = {
            "email": "",
            "otp": ""
        }
        response = self.client.post(self.url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"error": "Email and OTP are required."})