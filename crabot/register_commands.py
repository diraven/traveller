import os

import requests

import discord

url = f"https://discord.com/api/v8/applications/{os.environ['DISCORD_CLIENT_ID']}/guilds/{os.environ['DISCORD_GUILD_ID']}/commands"
headers = {"Authorization": f"Bot {os.environ['DISCORD_BOT_TOKEN']}"}
for definition in [
    {
        "name": "ping",
        "description": "Ping the bot1",
    },
    {
        "name": "games",
        "description": "Керування ігровими ролями",
        "options": [
            {
                "name": "list",
                "description": "Подивитися список ігрових ролей",
                "type": 1,
                "options": [
                    {
                        "name": "page",
                        "description": "Сторінка",
                        "type": discord.ApplicationCommandOptionType.INTEGER.value,
                    }
                ],
            },
            {
                "name": "join",
                "description": "Отримати ігрову роль",
                "type": 1,
                "options": [
                    {
                        "name": "role",
                        "description": "Роль",
                        "type": discord.ApplicationCommandOptionType.ROLE.value,
                        "required": True,
                    }
                ],
            },
            {
                "name": "leave",
                "description": "Зняти ігрову роль",
                "type": 1,
                "options": [
                    {
                        "name": "role",
                        "description": "Роль",
                        "type": discord.ApplicationCommandOptionType.ROLE.value,
                        "required": True,
                    }
                ],
            },
        ],
    },
]:
    r = requests.post(url, headers=headers, json=definition)
    print(r.json())
