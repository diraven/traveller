import os

import discord

intents = discord.Intents.default()
intents.members = True

DISCORD_BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]
GUILD_ID = int(os.environ["GUILD_ID"])
