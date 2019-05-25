# Create your views here.
import random
from collections import namedtuple

from allauth.socialaccount.models import SocialAccount, SocialApp
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from rest_framework.response import Response as DRFResponse
from rest_framework.views import APIView

from theburningclaw.models import Venture

Request = namedtuple('Request', [
    'service_name',
    'service_secret_key',
    'service_user_id',
    'display_name',
    'query',
])


class Response:
    def __init__(self):
        self.character = None
        self.events = []

    def add_event(self, text: str = ''):
        self.events.append(text)

    def drf(self):
        if not self.events:
            self.events += ['Nothing happened.']
        return DRFResponse({
            'character': str(self.character),
            'events': self.events,
        })


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

        resp = Response()

        # Get user and character.
        try:
            character = SocialAccount.objects.get(
                uid=req.service_user_id,
            ).user.character
        except SocialAccount.DoesNotExist:
            resp.add_event('Registration required.')
            return resp.drf()
        resp.character = character

        # Process request.
        action, arg = req.query.split(' ')
        if action == 'venture':
            try:
                venture = Venture.objects.get(slug=arg)
            except Venture.DoesNotExist:
                resp.add_event('Venture not found.')
                return resp.drf()

            luck = random.uniform(0, 1)
            for lootable in venture.lootable_set.filter(
                    chance__gte=1 - luck,
            ):
                count = random.randint(
                    lootable.count - lootable.count_deviation,
                    lootable.count + lootable.count_deviation + 1,
                )
                character.give(
                    (lootable.thing_kind, count),
                )
                resp.add_event(
                    f'You have looted {count} x {lootable.thing_kind}'
                )
            return resp.drf()

        return resp.drf()
