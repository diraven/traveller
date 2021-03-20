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
@discord_interactions.verify_key_decorator(app.config["PUBLIC_KEY"])
def interactions():
    request = flask.request.json
    interaction = discord.Interaction(**request)
    if interaction.type == discord.InteractionType.APPLICATION_COMMAND:

        if interaction.data["name"] == "ping":
            return api.new_interaction_response("Pong!")

        if interaction.data["name"] == "games":

            if interaction.data["options"][0]["name"] == "list":
                # TODO: List all public roles
                # TODO: Make sure to paginate the list
                try:
                    page = interaction.data["options"][0]["options"][0]["value"]
                except KeyError:
                    page = 1
                print(
                    api.get_page(map(lambda x: x["name"], api.get_public_roles())),
                    page,
                )
                return api.new_interaction_response("Games list!")

            if interaction.data["options"][0]["name"] == "join":
                # TODO: Make sure role is public
                # TODO: Assign role to person asking
                print(api.get_public_roles())
                return api.new_interaction_response("Games list!")

            if interaction.data["options"][0]["name"] == "leave":
                # TODO: Make sure role is public
                # TODO: Unassign role from person asking
                print(api.get_public_roles())
                return api.new_interaction_response("Games list!")

    raise RuntimeError(f"Unknown interaction: {interaction.data}")
