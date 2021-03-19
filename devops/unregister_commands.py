import os

import discord_interactions
import requests
from requests.api import delete, head

url = f"https://discord.com/api/v8/applications/{os.environ['DISCORD_CLIENT_ID']}/guilds/{os.environ['DISCORD_GUILD_ID']}/commands"
headers = {"Authorization": f"Bot {os.environ['DISCORD_BOT_TOKEN']}"}
r = requests.get(url, headers=headers)
for command in r.json():
    r = requests.delete(
        f"https://discord.com/api/v8/applications/{os.environ['DISCORD_CLIENT_ID']}/guilds/{os.environ['DISCORD_GUILD_ID']}/commands/{command['id']}",
        headers=headers,
    )
    print(r)
