# Create your views here.
from collections import namedtuple

from allauth.socialaccount.models import SocialAccount, SocialApp
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import APIView

Request = namedtuple('Request', [
    'service_name',
    'service_secret_key',
    'service_user_id',
    'display_name',
    'query',
])


class Do(APIView):
    permission_classes = []

    def post(self, request):
        """Process action posted by user."""
        # Validate request.
        try:
            req = Request(**{k: v for k, v in request.data.items()})
        except TypeError as e:
            raise ValidationError(str(e))

        # Validate secret key.
        try:
            SocialApp.objects.get(
                secret=req.service_secret_key,
            )
        except SocialAccount.DoesNotExist:
            raise AuthenticationFailed()

        # Get user and character.
        try:
            character = SocialAccount.objects.get(
                uid=req.service_user_id,
            ).user.character
        except SocialAccount.DoesNotExist:
            return Response('needs registeration')

        # Process request.

        return Response({
            "message": "Hello, world!",
            'character': str(character),
        })
