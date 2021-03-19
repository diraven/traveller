import os

import discord_interactions
import flask

from . import discord

PUBLIC_KEY = os.getenv("DISCORD_CLIENT_PUBLIC_KEY")

app = flask.Flask(__name__)


@app.route("/interactions/", methods=["POST"])
@discord_interactions.verify_key_decorator(PUBLIC_KEY)
def interactions():
    request = flask.request.json
    interaction = discord.Interaction(**request)
    if interaction.type == discord.InteractionType.APPLICATION_COMMAND:

        if interaction.data["name"] == "ping":
            return discord.interaction_response("Pong!")

        if interaction.data["name"] == "games":

            if interaction.data["options"][0]["name"] == "list":
                # TODO: List all public roles
                # TODO: Make sure to paginate the list
                print(discord.get_public_roles())
                return discord.interaction_response("Games list!")

            if interaction.data["options"][0]["name"] == "join":
                # TODO: Make sure role is public
                # TODO: Assign role to person asking
                print(discord.get_public_roles())
                return discord.interaction_response("Games list!")

            if interaction.data["options"][0]["name"] == "leave":
                # TODO: Make sure role is public
                # TODO: Unassign role from person asking
                print(discord.get_public_roles())
                return discord.interaction_response("Games list!")

    raise RuntimeError(f"Unknown interaction: {interaction.data}")
