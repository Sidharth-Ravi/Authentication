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



