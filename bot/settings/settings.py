DEBUG = True

DISCORD_TOKEN = ''
DISCORD_DEFAULT_PREFIX = '.'

RAVEN_CONFIG = ""

DB_USER = ""
DB_PASSWORD = ""
DB_NAME = ""

try:
    from .settings_local import *
except ImportError:
    pass
