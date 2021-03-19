import os

import discord_interactions
import requests

url = f"https://discord.com/api/v8/applications/{os.environ['DISCORD_CLIENT_ID']}/guilds/{os.environ['DISCORD_GUILD_ID']}/commands"
print(url)
json = {
    "name": "ping",
    "description": "Ping the bot1",
}
headers = {"Authorization": f"Bot {os.environ['DISCORD_BOT_TOKEN']}"}
r = requests.post(url, headers=headers, json=json)
print(r.json())
