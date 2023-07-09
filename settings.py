import os

import discord

intents = discord.Intents.default()
intents.members = True

DISCORD_BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]
