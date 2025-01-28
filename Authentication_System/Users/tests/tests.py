import unittest
from unittest.mock import MagicMock, patch

from django.conf import settings

from Authentication_System.Users.schema import Mutation


class TestMutation(unittest.TestCase):

    @patch('Authentication_System.Users.schema.CustomUser')
    def test_register_user_email_exists(self, MockCustomUser):
        # Mock the objects.filter().exists() method to return True
        MockCustomUser.objects.filter.return_value.exists.return_value = True

        mutation = Mutation()
        with self.assertRaises(Exception) as context:
            mutation.register_user(email="test@example.com", password="password123")

        self.assertEqual(str(context.exception), "Email already exists.")

    @patch('Authentication_System.Users.schema.CustomUser')
    @patch('Authentication_System.Users.schema.send_mail')
    @patch('Authentication_System.Users.schema.generate_otp')
    def test_register_user_success(self, mock_generate_otp, mock_send_mail, MockCustomUser):
        # Mock the objects.filter().exists() method to return False
        MockCustomUser.objects.filter.return_value.exists.return_value = False

        # Mock the create_user method
        MockCustomUser.objects.create_user = MagicMock(return_value=MockCustomUser)

        # Mock the generate_otp function
        mock_generate_otp.return_value = "123456"

        mutation = Mutation()
        result = mutation.register_user(email="test@example.com", password="password123")

        # Check if create_user was called with the correct parameters
        MockCustomUser.objects.create_user.assert_called_with(email="test@example.com", password="password123")

        # Check if send_mail was called with the correct parameters
        mock_send_mail.assert_called_with(
            subject="Your Registration OTP",
            message="Your OTP is: 123456",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=["test@example.com"],
            fail_silently=False
        )

        self.assertEqual(result, "User registered successfully. Please verify your account using the OTP sent to your email.")

    @patch('Authentication_System.Users.schema.CustomUser')
    def test_verify_otp_success(self, MockCustomUser):
        # Mock the get method to return a user with a valid OTP
        mock_user = MagicMock()
        mock_user.is_otp_valid.return_value = True
        MockCustomUser.objects.get.return_value = mock_user

        mutation = Mutation()
        result = mutation.verify_otp(info=None, email="test@example.com", otp="123456")

        # Check if the user's is_active, otp, and otp_expiration fields were updated
        self.assertTrue(mock_user.is_active)
        self.assertIsNone(mock_user.otp)
        self.assertIsNone(mock_user.otp_expiration)
        mock_user.save.assert_called_once()

        self.assertEqual(result, "OTP verified successfully. Account activated.")

    @patch('Authentication_System.Users.schema.CustomUser')
    def test_verify_otp_invalid(self, MockCustomUser):
        # Mock the get method to return a user with an invalid OTP
        mock_user = MagicMock()
        mock_user.is_otp_valid.return_value = False
        MockCustomUser.objects.get.return_value = mock_user

        mutation = Mutation()
        with self.assertRaises(Exception) as context:
            mutation.verify_otp(info=None, email="      ", otp="123456")







import unittest
from unittest.mock import patch, MagicMock
from Authentication_System.Users.schema import Mutation

class TestMutation(unittest.TestCase):

    @patch('Authentication_System.Users.schema.CustomUser')
    @patch('Authentication_System.Users.schema.send_mail')
    @patch('Authentication_System.Users.schema.generate_otp')
    def test_forgot_password_user_exists(self, mock_generate_otp, mock_send_mail, MockCustomUser):
        mock_generate_otp.return_value = '123456'
        mock_user = MagicMock()
        MockCustomUser.objects.get.return_value = mock_user

        mutation = Mutation()
        response = mutation.forgot_password(email="test@example.com")

        mock_user.save.assert_called_once()
        mock_send_mail.assert_called_once()
        self.assertEqual(response, "Link for resetting password has been send successfully")

    @patch('Authentication_System.Users.schema.CustomUser')
    def test_forgot_password_user_not_found(self, MockCustomUser):
        MockCustomUser.objects.get.side_effect = MockCustomUser.DoesNotExist

        mutation = Mutation()
        with self.assertRaises(Exception) as context:
            mutation.forgot_password(email="nonexistent@example.com")

        self.assertEqual(str(context.exception), "User not found.")

if __name__ == '__main__':
    unittest.main()







    import json
from django.test import TestCase, Client
from django.urls import reverse
from Users.models import CustomUser
from rest_framework import status
from django.contrib.auth.hashers import make_password

class TestResetPasswordView(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('reset_password')
        self.user = CustomUser.objects.create(
            email="test@example.com",
            password=make_password("current_password")
        )

    def test_reset_password_success(self):
        data = {
            "email": "test@example.com",
            "current_password": "current_password",
            "new_password": "new_password123"
        }
        response = self.client.post(self.url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"message": "Password set successfully"})

    def test_reset_password_invalid_current_password(self):
        data = {
            "email": "test@example.com",
            "current_password": "wrong_password",
            "new_password": "new_password123"
        }
        response = self.client.post(self.url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"error": "Invalid current password"})

    def test_reset_password_same_as_current(self):
        data = {
            "email": "test@example.com",
            "current_password": "current_password",
            "new_password": "current_password"
        }
        response = self.client.post(self.url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"error": "New password cannot be the same as the current password."})

    def test_reset_password_invalid_email(self):
        data = {
            "email": "invalid@example.com",
            "current_password": "current_password",
            "new_password": "new_password123"
        }
        response = self.client.post(self.url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json(), {"error": "Invalid email"})








import unittest
from unittest.mock import patch, MagicMock
from Authentication_System.Users.schema import Mutation

class TestMutation(unittest.TestCase):

    @patch('Authentication_System.Users.schema.CustomUser')
    def test_update_profile_success(self, MockCustomUser):
        mock_user = MagicMock()
        MockCustomUser.objects.get.return_value = mock_user

        mutation = Mutation()
        response = mutation.update_profile(first_name="John", last_name="Doe", email="test@example.com")

        mock_user.save.assert_called_once()
        self.assertEqual(response, "Profile updated successfully")

    @patch('Authentication_System.Users.schema.CustomUser')
    def test_update_profile_user_not_found(self, MockCustomUser):
        MockCustomUser.objects.get.side_effect = MockCustomUser.DoesNotExist

        mutation = Mutation()
        with self.assertRaises(Exception) as context:
            mutation.update_profile(first_name="John", last_name="Doe", email="nonexistent@example.com")

        self.assertEqual(str(context.exception), "User not found.")

if __name__ == '__main__':
    unittest.main()







    
