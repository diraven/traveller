import os

import discord

intents = discord.Intents.default()
intents.members = True

DEBUG = os.getenv("DEBUG") == "True"
DISCORD_BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]
SENTRY_DSN = os.getenv("SENTRY_DSN")
