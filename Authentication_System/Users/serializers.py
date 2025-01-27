from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        # Authenticate user
        user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        
        # Ensure the user's email is verified
        if not user.is_email_verified:
            raise serializers.ValidationError("Email is not verified. Please verify your email first.")
        
        self.user = user
        return data

    def get_tokens(self):
        refresh = RefreshToken.for_user(self.user)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }
