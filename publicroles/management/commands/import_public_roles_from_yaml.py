import re

from django.core.management.base import BaseCommand

from mydiscord.models import Guild
from publicroles.models import PublicRole


class Command(BaseCommand):
    help = 'Starts discord bot.'

    def add_arguments(self, parser) -> None:
        parser.add_argument('guild_uid')

    def handle(self, *args, **options) -> None:
        guild = Guild.objects.get(uid=options['guild_uid'])

        with open('public_roles.yaml', 'r') as file:
            for line in file.read().splitlines():
                PublicRole.objects.get_or_create(
                    guild=guild,
                    uid=re.findall(r'^- "(\d+)"', line)[0])
