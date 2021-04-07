import os

import discord_interactions
import flask

from . import discord

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

api = discord.Api(
    guild_id=app.config["DISCORD_GUILD_ID"],
    bot_token=app.config["DISCORD_BOT_TOKEN"],
)


@app.route("/interactions/", methods=["POST"])
@discord_interactions.verify_key_decorator(app.config["DISCORD_CLIENT_PUBLIC_KEY"])
def interactions():
    request = flask.request.json
    interaction = discord.Interaction(**request)
    if interaction.type == discord.InteractionType.APPLICATION_COMMAND:

        if interaction.data["name"] == "ping":
            return api.new_interaction_response("Pong!")

        if interaction.data["name"] == "games":
            public_roles = api.get_public_roles()

            def is_public(role_id):
                return role_id in [role["id"] for role in public_roles]

            # List public roles.
            if interaction.data["options"][0]["name"] == "list":
                try:
                    page_num = interaction.data["options"][0]["options"][0]["value"]
                except KeyError:
                    page_num = 1
                page_content, page_count = api.get_page(
                    map(lambda x: x["name"], public_roles), page_num
                )
                return api.info(
                    text=f"{page_content}",
                    footer=f"Сторінка {min(page_num, page_count)}/{page_count}",
                )

            # The rest of the commands are for public roles only.
            role_id = interaction.data["options"][0]["options"][0]["value"]
            if not is_public(role_id):
                return api.error(
                    text=f"Роль <@&{role_id}> не є публічною.",
                )

            # Get public role.
            if interaction.data["options"][0]["name"] == "join":
                api.member_add_role(interaction.member.user.id, role_id)
                return api.success(
                    text=f"Роль <@&{role_id}> додано.",
                )

            # Get rid of public role.
            if interaction.data["options"][0]["name"] == "leave":
                api.member_remove_role(interaction.member.user.id, role_id)
                return api.success(
                    text=f"Роль <@&{role_id}> знято.",
                )

            # List players.
            if interaction.data["options"][0]["name"] == "play":
                # TODO: List members that have given role
                pass

    raise RuntimeError(f"Unknown interaction: {interaction.data}")
