import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

User = get_user_model()

class GoogleLoginView(APIView):

    def post(self, request):
        code = request.data.get('code')
        if not code:
            return Response({"error": "Code is required"}, status=400)

        token_response = requests.post(
            'https://oauth2.googleapis.com/token',
            data={
                'code': code,
                'client_id': '901831003903-csvdkgruqic01k6eiqus7jfeimen09g5.apps.googleusercontent.com',
                "client_secret": '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',
                'redirect_uri': 'http://localhost:8000/api/v1/users/google-login',
                'grant_type': 'authorization_code'
            }
        )

        token_response = token_response.json()
        access_token = token_response.get('access_token')

        if not access_token:
            return Response({"error": "Failed to obtain access token"}, status=400)

        user_info_response = requests.get(
            'https://www.googleapis.com/oauth2/v1/userinfo',
            params={'alt': 'json'},
            headers={'Authorization': f'Bearer {access_token}'}

        )
        print(f'User info response: {user_info_response.json()}')

        email = user_info_response.json().get('email')
        first_name = user_info_response.json().get('given_name')
        last_name = user_info_response.json().get('family_name')

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'username': email.split('@')[0]
            }
        )

        refresh = RefreshToken.for_user(user)
        refresh['email'] = user.email

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'username': user.username
            }
        })
