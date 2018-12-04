from django.core.management.base import BaseCommand

from mydiscord.bot import bot
from project import settings


class Command(BaseCommand):
    help = 'Starts discord bot.'

    def handle(self, *args, **options) -> None:
        """
        Django management command handler.
        """

        bot.run(settings.DISCORD_TOKEN)
