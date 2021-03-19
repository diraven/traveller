import dataclasses
import datetime
import enum
import os
import typing as t

import dateutil.parser
import discord_interactions
import flask

PUBLIC_KEY = os.getenv("DISCORD_CLIENT_PUBLIC_KEY")

app = flask.Flask(__name__)


@enum.unique
class InteractionType(enum.Enum):
    PING = 1
    APPLICATION_COMMAND = 2


@enum.unique
class ResponseType(enum.Enum):
    PONG = 1
    CHANNEL_MESSAGE_WITH_SOURCE = 4
    DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE = 5


@dataclasses.dataclass
class User:
    avatar: str
    discriminator: str
    id: str
    public_flags: int
    username: str


@dataclasses.dataclass
class Member:
    deaf: bool
    is_pending: bool
    joined_at: dataclasses.InitVar[datetime.datetime]
    mute: bool
    nick: t.Optional[str]
    pending: bool
    permissions: str
    premium_since: t.Optional[str]
    roles: t.List[str]
    user: dataclasses.InitVar[User]

    def __post_init__(self, joined_at, user):
        self.user = User(**user)
        self.joined_at = dateutil.parser.parse(joined_at)


@dataclasses.dataclass
class Interaction:
    application_id: str
    channel_id: str
    data: t.Dict
    guild_id: str
    id: str
    member: dataclasses.InitVar[Member]
    token: str
    type: dataclasses.InitVar[InteractionType]
    version: str
    name: t.Optional[str] = None

    def __post_init__(self, member, type_):
        self.member = Member(**member)
        self.type = InteractionType(type_)

        self.name = self.data["name"]


def response(text: str):
    return flask.jsonify(
        {
            "type": ResponseType.CHANNEL_MESSAGE_WITH_SOURCE.value,
            "data": {"content": text},
        }
    )


@app.route("/interactions/", methods=["POST"])
@discord_interactions.verify_key_decorator(PUBLIC_KEY)
def interactions():
    interaction = Interaction(**flask.request.json)
    if interaction.type == InteractionType.APPLICATION_COMMAND:

        if interaction.name == "ping":
            return response("Pong!")

    raise RuntimeError(f"Unknown interaction name: {interaction.name}")
