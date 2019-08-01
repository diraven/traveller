"""Management command to allow CI to migrate database back to zero state."""

from django.core.management.base import BaseCommand  # pragma: no cover
from django.core import management  # pragma: no cover
from django.apps import apps  # pragma: no cover


class Command(BaseCommand):  # pragma: no cover
    """Migrate the whole database downwards to the zero state."""

    help = 'Migrates the whole database downwards to the zero state.'  # noqa

    def add_arguments(self, parser):
        """Add arguments."""
        parser.add_argument(
            '--noinput', '--no-input',
            action='store_false',
            dest='interactive',
            help='Tells Django to NOT prompt the user for input of any kind.',
        )

    def handle(self, *args, **kwargs):
        """Handle command execution."""
        interactive = kwargs['interactive']

        if interactive:
            confirm = input(  # noqa: S322
                """
You have requested a flush of the database. This will IRREVERSIBLY DESTROY
all data and structure currently in the database. Are you sure you want to do
this?

Type 'yes' to continue, or 'no' to cancel:
""",
            )
        else:
            confirm = 'yes'

        if confirm == 'yes':
            for app_name, app_config in apps.app_configs.items():
                if app_config.models and app_name != 'corsheaders':
                    management.call_command('migrate', app_name, 'zero')
                    management.call_command(
                        'migrate',
                        '--database=userdata',
                        app_name,
                        'zero',
                    )
                    management.call_command(
                        'migrate',
                        '--database=knowledge',
                        app_name,
                        'zero',
                    )
        else:
            self.stdout.write('Migration to zero state cancelled.\n')
