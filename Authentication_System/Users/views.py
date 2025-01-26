from django.shortcuts import render
from strawberry.django.views import GraphQLView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.test import RequestFactory
from Users.models import CustomUser
from .schema import schema


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





