"""Bot settings module."""
import os

DEBUG = os.getenv('DEBUG') == 'True'

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
DISCORD_DEFAULT_PREFIX = os.getenv('DISCORD_DEFAULT_PREFIX')

SENTRY_DSN = os.getenv('SENTRY_DSN')
