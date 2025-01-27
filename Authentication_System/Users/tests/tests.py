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