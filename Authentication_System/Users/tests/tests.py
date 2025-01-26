import unittest
from ..schema import generate_otp

# FILE: Authentication_System/Users/test_schema.py


class TestGenerateOtp(unittest.TestCase):

    def test_generate_otp_length(self):
        otp = generate_otp()
        self.assertEqual(len(otp), 6, "OTP length should be 6")

    def test_generate_otp_digits(self):
        otp = generate_otp()
        self.assertTrue(otp.isdigit(), "OTP should contain only digits")

if __name__ == '__main__':
    unittest.main()