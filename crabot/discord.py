import dataclasses
import datetime
import enum
import os
import pprint
import typing as t

import dateutil.parser
import flask
import requests
from requests.sessions import CaseInsensitiveDict

API_VERSION = "8"
BASE_API_URL = "https://discord.com/api"
API_URL = f"{BASE_API_URL}/v{API_VERSION}"
GUILD_API_URL = f"{API_URL}/guilds/{os.environ['DISCORD_GUILD_ID']}"

client = requests.session()
client.headers = CaseInsensitiveDict(
    {"Authorization": f"Bot {os.environ['DISCORD_BOT_TOKEN']}"}
)


@enum.unique
class ApplicationCommandOptionType(enum.Enum):
    SUB_COMMAND = 1
    SUB_COMMAND_GROUP = 2
    STRING = 3
    INTEGER = 4
    BOOLEAN = 5
    USER = 6
    CHANNEL = 7
    ROLE = 8


@enum.unique
class InteractionType(enum.Enum):
    PING = 1
    APPLICATION_COMMAND = 2


@enum.unique
class InteractionResponseType(enum.Enum):
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

    def __post_init__(self, member, type_):
        self.member = Member(**member)
        self.type = InteractionType(type_)


def interaction_response(text: str):
    return flask.jsonify(
        {
            "type": InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE.value,
            "data": {"content": text},
        }
    )


def get_public_roles():
    response = client.get(f"{GUILD_API_URL}/roles")
    all_roles = response.json()
    marker_seen = False
    public_roles = []
    for role in all_roles:
        if marker_seen:
            public_roles.append(role)
            continue
        marker_seen = role["name"] == "public-roles"
    return public_roles
