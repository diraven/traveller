"""Bot settings module."""
import os

DEBUG = os.getenv('DEBUG') == 'True'

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
DISCORD_DEFAULT_PREFIX = os.getenv('DISCORD_DEFAULT_PREFIX')

RAVEN_CONFIG = os.getenv('RAVEN_CONFIG')

DB_USER = os.getenv('POSTGRES_DB')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD')
DB_NAME = os.getenv('POSTGRES_USER')
DB_HOST = os.getenv('POSTGRES_HOST')
