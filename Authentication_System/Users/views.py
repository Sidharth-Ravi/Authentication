from django.shortcuts import render
from strawberry.django.views import GraphQLView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.test import RequestFactory
from Users.models import CustomUser
from .schema import schema
from .serializers import LoginSerializer


@csrf_exempt
def register_user(request):
    if request.method == "POST":
        try:
            # Parse the request body as JSON
            body = json.loads(request.body)

            # Construct the GraphQL mutation query
            query = """
                mutation($email: String!, $password: String!) {
                    registerUser(email: $email, password: $password)
                }
            """
            variables = {
                "email": body.get("email"),
                "password": body.get("password"),

            }

            if not variables["email"] or not variables["password"]:
                return JsonResponse({"error": "Email and password are required."}, status=400)

            # Create a mock POST request using RequestFactory
            rf = RequestFactory()
            graphql_request_data = {
                "query": query,
                "variables": variables,
            }
            req = rf.post('/api/register/', json.dumps(graphql_request_data), content_type='application/json')

            # Create a GraphQL view to process the request
            graphql_view = GraphQLView.as_view(schema=schema)
            response = graphql_view(req)

            # Return the response as a JSON object
            return JsonResponse(json.loads(response.content), safe=False)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "POST method required"}, status=405)


@csrf_exempt
def verify_otp(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            email = body.get("email")
            otp = body.get("otp")

            if not email or not otp:
                return JsonResponse({"error": "Email and OTP are required."}, status=400)

            try:
                user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                return JsonResponse({"error": "User not found."}, status=404)

            if user.is_otp_valid(otp):
                user.is_active = True
                user.otp = None
                user.otp_expiration = None
                user.is_email_verified = True
                user.save()
                return JsonResponse({"message": "OTP verified successfully. Account activated."}, status=200)
            else:
                return JsonResponse({"error": "Invalid or expired OTP."}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "POST method required"}, status=405)





@csrf_exempt
def login(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            serializer = LoginSerializer(data=data)

            if serializer.is_valid():
                tokens = serializer.get_tokens()
                return JsonResponse(tokens, status=200)
            return JsonResponse(serializer.errors, status=400)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format."}, status=400)

    return JsonResponse({"error": "POST method required"}, status=405)






from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from Users.models import CustomUser
from django.utils.crypto import get_random_string
from django.conf import settings
from django.http import JsonResponse
from django.test import RequestFactory
from strawberry.django.views import GraphQLView
from .schema import schema
import json


class ForgotPassword(APIView):
    def post(self, request):
        try:
            # Parse the request body
            body = request.data
            
            
            # Extract email from the request body
            email = body.get("email")
            if not email:
                return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

            # Check if the user exists
            try:
                user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)
            
            query = """
                mutation($email: String!) {
                    forgotPassword(email: $email)
                }
            """
            variables = {
                "email": body.get("email"),
            }

            rf = RequestFactory()
            graphql_request_data = {
                "query": query,
                "variables": variables,
            }
            req = rf.post('/api/forgotPassword/', json.dumps(graphql_request_data), content_type='application/json')

            # Create a GraphQL view to process the request
            graphql_view = GraphQLView.as_view(schema=schema)
            response = graphql_view(req)

            # Return the response as a JSON object
            return Response({"message": "Password reset token sent to your email."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)







from strawberry.django.views import GraphQLView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.test import RequestFactory
from Users.models import CustomUser
from .schema import schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import OutstandingToken, BlacklistedToken
from .serializers import LoginSerializer
from django.contrib.auth.hashers import check_password

class ResetPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')

        try:
            user = CustomUser.objects.get(email=email)
            if not check_password(current_password, user.password):
                return Response({"error": "Invalid current password"}, status=status.HTTP_400_BAD_REQUEST)
            
            if check_password(new_password, user.password):
                return Response({"error": "New password cannot be the same as the current password."},
                                status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(new_password) 
            user.save()
            return Response({"message": "Password set successfully"}, status=status.HTTP_200_OK)
        
        except CustomUser.DoesNotExist:
            return Response({"error": "Invalid email"}, status=status.HTTP_404_NOT_FOUND)
        










from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import ModelSerializer
from django.contrib.auth.models import User
from strawberry.django.views import GraphQLView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.test import RequestFactory
from Users.models import CustomUser
from .schema import schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import OutstandingToken, BlacklistedToken
from .serializers import LoginSerializer

@csrf_exempt
def UpdateProfileView(request):
    if request.method == "PUT":
        try:
            # Parse the request body as JSON
            body = json.loads(request.body)

            # Construct the GraphQL mutation query
            query = """
                mutation($first_name: String!, $last_name: String!, $email: String!) {
                    updateProfile(firstName: $first_name, lastName: $last_name, email: $email)
                }
            """
            variables = {
                "first_name": body.get("first_name"),
                "last_name": body.get("last_name"),
                "email": body.get("email"),
            }

            if not any(variables.values()):
                return JsonResponse({"error": "At least one field (first_name, last_name, email) is required."}, status=400)

            # Create a mock POST request using RequestFactory
            rf = RequestFactory()
            graphql_request_data = {
                "query": query,
                "variables": variables,
            }
            req = rf.post('/api/update-profile/', json.dumps(graphql_request_data), content_type='application/json')

            # Create a GraphQL view to process the request
            graphql_view = GraphQLView.as_view(schema=schema)
            response = graphql_view(req)

            # Return the response as a JSON object
            return JsonResponse(json.loads(response.content), safe=False)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "PUT method required"}, status=405)









from strawberry.django.views import GraphQLView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.test import RequestFactory
from Users.models import CustomUser
from .schema import schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import OutstandingToken, BlacklistedToken
from .serializers import LoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken

@csrf_exempt
def logout(request):
    permission_classes = [IsAuthenticated]
    try:
        # Blacklist the latest token for the user
        body = json.loads(request.body)
        email = body.get('email')
        user = CustomUser.objects.get(email=email)
        outstanding_tokens = OutstandingToken.objects.filter(user=user)
        latest_token = outstanding_tokens.latest('created_at')
        BlacklistedToken.objects.create(token=latest_token)
        return JsonResponse({"message": "Logout successful"}, status=status.HTTP_200_OK)
    except CustomUser.DoesNotExist: 
        return JsonResponse({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

