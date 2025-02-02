# authentication/models.py
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.timezone import now, timedelta

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, null=True, blank=True)
    otp_expiration = models.DateTimeField(null=True, blank=True)
    is_email_verified = models.BooleanField(default=False)
    
    
    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def set_otp(self):
        from random import randint
        self.otp = f"{randint(100000, 999999)}"  # Generate a 6-digit OTP
        self.otp_expiration = now() + timedelta(minutes=10)
        self.save()

    def is_otp_valid(self, otp):
        if self.otp_expiration is None:
            return False 
        return self.otp == otp and self.otp_expiration > now()