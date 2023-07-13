import logging
import os

import discord

logging.getLogger().setLevel(logging.INFO)

intents = discord.Intents.default()
intents.members = True

DISCORD_BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]
DEBUG = os.getenv("DEBUG") == "True"
SENTRY_DSN = os.getenv("SENTRY_DSN")
DISCORD_DEV_GUILD_ID = int(os.getenv("DISCORD_DEV_GUILD_ID", "0"))
