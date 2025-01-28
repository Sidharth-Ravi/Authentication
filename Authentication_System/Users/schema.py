import strawberry
from django.core.mail import send_mail
from django.conf import settings
from .models import CustomUser
import random
import string
from strawberry.types import Info
from datetime import timedelta
from django.utils.timezone import now

# Utility function to generate OTP
def generate_otp():
    return ''.join(random.choices(string.digits, k=6))  # Generate a 6-digit OTP


# Mutation for registering a user
@strawberry.type
class Mutation:
    @strawberry.mutation
    def register_user(self, email: str, password: str) -> str:
        # Check if the email already exists
        if CustomUser.objects.filter(email=email).exists():
            raise Exception("Email already exists.")

        # Create user and generate OTP
        user = CustomUser.objects.create_user(email=email, password=password)
        otp = generate_otp()
        otp_expiration = now() + timedelta(minutes=30)

        # Send verification email
        send_mail(
            subject="Your Registration OTP",
            message=f"Your OTP is: {otp}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently = False
        )

        # Save OTP in the user (you might want to handle this more securely)
        user.otp = otp
        user.otp_expiration = otp_expiration
        user.is_active = False  # Deactivate until verification
        user.save()

        return "User registered successfully. Please verify your account using the OTP sent to your email."
    




    @strawberry.mutation
    def verify_otp(self, info: Info, email: str, otp: str) -> str:
        """
        Verify the OTP sent to the user's email and activate the account.
        """
        try:
            user = CustomUser.objects.get(email=email)
            if user.is_otp_valid(otp):
                user.is_active = True
                user.otp = None
                user.otp_expiration = None
                user.save()
                return "OTP verified successfully. Account activated."
            else:
                raise Exception("Invalid or expired OTP.")
        except CustomUser.DoesNotExist:
            raise Exception("User not found.")




    @strawberry.mutation
    def forgot_password(email: str) -> str:


        user = CustomUser.objects.get(email=email)
        otp = generate_otp()
        otp_expiration = now() + timedelta(minutes=30)

        message = f"""
            Hi {user.email},
                Here is your password reset otp: {otp}
                Use this token to reset your password. If you didn't request this, please ignore this email.
                """ 

        # Send verification email
        send_mail(
            subject="OTP for resetting password",
            message = message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )

        # Save OTP in the user (you might want to handle this more securely)
        user.otp = otp
        user.otp_expiration = otp_expiration
        user.save()

        return "Link for resetting password has been send successfully"






    @strawberry.mutation
    def update_profile(self, first_name: str, last_name: str, email: str) -> str:

        try:
            user = CustomUser.objects.get(email=email)
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            return "Profile updated successfully"
        except CustomUser.DoesNotExist:
            raise Exception("User not found.")











    
    # Minimal Query type (placeholder)
@strawberry.type
class Query:
    hello: str = "Hello, world!"

    
# Create the schema
schema = strawberry.Schema(query=Query, mutation=Mutation)

