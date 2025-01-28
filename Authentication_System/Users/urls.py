from django.urls import path
from . import views

urlpatterns = [
    path('register', views.register_user, name='register'), 
    path("verify-otp", views.verify_otp, name="verify_otp"),
    path('login', views.login, name='login'),
    path('forgot-password', views.ForgotPassword.as_view(), name='forgot_password'),
    
]