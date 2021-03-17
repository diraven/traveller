import os

import discord_interactions
import flask

PUBLIC_KEY = os.getenv("DISCORD_CLIENT_PUBLIC_KEY")

app = flask.Flask(__name__)


@app.route("/interactions/", methods=["POST"])
@discord_interactions.verify_key_decorator(PUBLIC_KEY)
def interactions():
    if (
        flask.request.json["type"]
        == discord_interactions.InteractionType.APPLICATION_COMMAND
    ):
        return flask.jsonify(
            {
                "type": discord_interactions.InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                "data": {"content": "Hello world"},
            }
        )
    return None
