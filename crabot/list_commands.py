import os

import discord_interactions
import requests

url = f"https://discord.com/api/v8/applications/{os.environ['DISCORD_CLIENT_ID']}/guilds/{os.environ['DISCORD_GUILD_ID']}/commands"
headers = {"Authorization": f"Bot {os.environ['DISCORD_BOT_TOKEN']}"}
r = requests.get(url, headers=headers)
print(r.json())
