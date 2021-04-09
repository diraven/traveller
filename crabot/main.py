import os

import discord_interactions
import flask
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

from .api import Api

sentry_sdk.init(
    dsn=os.environ["SENTRY_DSN"],
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0,
)

app = flask.Flask(__name__)

if not app.config["TESTING"]:
    app.config.update(
        {
            "DISCORD_BOT_TOKEN": os.environ["DISCORD_BOT_TOKEN"],
            "DISCORD_CLIENT_ID": os.environ["DISCORD_CLIENT_ID"],
            "DISCORD_CLIENT_PUBLIC_KEY": os.environ["DISCORD_CLIENT_PUBLIC_KEY"],
            "DISCORD_GUILD_ID": os.environ["DISCORD_GUILD_ID"],
        }
    )

api = Api(
    guild_id=app.config["DISCORD_GUILD_ID"],
    bot_token=app.config["DISCORD_BOT_TOKEN"],
)


@app.route("/interactions/", methods=["POST"])
@discord_interactions.verify_key_decorator(app.config["DISCORD_CLIENT_PUBLIC_KEY"])
def interactions():
    request = flask.request.json
    interaction = api.parse_interaction(request)
    if interaction.type == interaction.Type.APPLICATION_COMMAND:

        if interaction.data["name"] == "ping":
            return api.info("Pong!")

        if interaction.data["name"] == "games":
            # List public roles.
            if interaction.data["options"][0]["name"] == "list":
                try:
                    page_num = interaction.data["options"][0]["options"][0]["value"]
                except KeyError:
                    page_num = 1
                if page_num < 1:
                    page_num = 1
                page_content, page_count = api.get_page(
                    map(lambda x: x.name, api.public_roles), page_num
                )
                return api.info(
                    text=f"{page_content}",
                    footer=f"Сторінка {min(page_num, page_count)}/{page_count}",
                )

            # The rest of the commands are for public roles only.
            role_id = interaction.data["options"][0]["options"][0]["value"]
            try:
                role = api.get_public_role(role_id)
            except StopIteration:
                return api.error(
                    text=f"Роль <@&{role_id}> не є публічною.",
                )

            # Get public role.
            if interaction.data["options"][0]["name"] == "join":
                api.member_add_role(interaction.member, role)
                return api.success(
                    text=f"Роль {role} додано.",
                )

            # Get rid of public role.
            if interaction.data["options"][0]["name"] == "leave":
                api.member_remove_role(interaction.member, role)
                return api.success(
                    text=f"Роль {role} знято.",
                )

            # List players.
            if interaction.data["options"][0]["name"] == "play":
                playing_members = filter(
                    lambda member: role.id in member.roles, api.guild_members
                )
                page_content, page_count = api.get_page(
                    [str(member) for member in playing_members]
                )
                return api.success(
                    title=f"Грають в {role.name}",
                    text=page_content or "Ніхто"
                    if page_count == 1
                    else f"{page_content} та інші...",
                )

    raise RuntimeError(f"Unknown interaction: {interaction.data}")
