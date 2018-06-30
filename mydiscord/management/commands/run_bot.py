from django.core.management.base import BaseCommand

from mydiscord.bot import bot


class Command(BaseCommand):
    help = 'Starts discord bot.'

    def add_arguments(self, parser) -> None:
        """
        Django management commands arguments setting.
        """
        parser.add_argument('token')

    def handle(self, *args, **options) -> None:
        """
        Django management command handler.
        """

        bot.run(options['token'])
