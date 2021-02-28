import requests
import os
import sys

from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = os.getenv("DISCORD_GUILD_ID")

client = requests.session()
client.headers.update({"Authorization": f"Bot {BOT_TOKEN}"})

URL = f"https://discord.com/api/v8/applications/{CLIENT_ID}/guilds/{GUILD_ID}/commands"

arguments = sys.argv[1:]
if len(arguments) == 0:
    r = client.get(URL)
    print(r.text)
else:
    action, argument = sys.argv[1:]

    if action == "add":
        payload = {
            "name": argument,
            "description": "Send a random adorable animal photo",
            "options": [
                {
                    "name": "animal",
                    "description": "The type of animal",
                    "type": 3,
                    "required": True,
                    "choices": [
                        {"name": "Dog", "value": "animal_dog"},
                        {"name": "Cat", "value": "animal_cat"},
                        {"name": "Penguin", "value": "animal_penguin"},
                    ],
                },
                {
                    "name": "only_smol",
                    "description": "Whether to show only baby animals",
                    "type": 5,
                    "required": False,
                },
            ],
        }
        r = client.post(URL, json=payload)
        print(r.text)

    if action == "del":
        r = client.delete(f"{URL}/{argument}")
        print(r.text)
