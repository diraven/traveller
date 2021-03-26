import dataclasses
import datetime
import enum
import typing as t

import dateutil.parser
import flask
import requests
from requests.sessions import CaseInsensitiveDict


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
class Member:  # pylint: disable=too-many-instance-attributes
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
class Interaction:  # pylint: disable=too-many-instance-attributes
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


class Api:
    def __init__(self, guild_id: str, bot_token: str, version="8"):
        self.base_api_url = "https://discord.com/api"

        self.version = version
        self.guild_id = guild_id
        self.bot_token = bot_token

        self.api_url = f"{self.base_api_url}/v{self.version}"
        self.guild_api_url = f"{self.api_url}/guilds/{guild_id}"

        self.client = requests.session()
        self.client.headers = CaseInsensitiveDict(
            {"Authorization": f"Bot {self.bot_token}"}
        )

    @staticmethod
    def new_interaction_response(text: str, title: str = "", footer: str = ""):
        return flask.jsonify(
            {
                "type": InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE.value,
                "data": {
                    "embeds": [
                        Api.new_embed(description=text, title=title, footer=footer)
                    ],
                },
            }
        )

    @staticmethod
    def new_embed(
        description: str,
        title: str,
        footer: str,
        # url,
        # timestamp,
        # color,
        # footer,
        # image,
        # thumbnail,
        # video,
        # provider,
        # author,
        # fields,
    ):
        return {
            "description": description,
            "title": title,
            "footer": {"text": footer, "icon_url": "", "proxy_icon_url": ""},
            # "type": "rich",
            # "": "",
            # "timestamp": "",
            # "color": "",
            # "author": {
            #     "name": "",
            #     "url": "",
            #     "icon_url": "",
            #     "proxy_icon_url": "",
            # },
            # "fields": [
            #     {
            #         "name": "",
            #         "value": "",
            #         "inline": "",
            #     }
            # ],
        }

    @staticmethod
    def get_page(items: t.Iterable[str], page_num: int = 1) -> t.Tuple[str, int]:
        items = [i for i in items]
        separator = " **|** "
        max_page_len = 100
        pages: t.List[str] = []

        length = 0
        start = 0
        for i, item in enumerate(items):
            delta = len(separator) + len(item)
            if length + delta > max_page_len:
                pages.append(separator.join(items[start:i]))
                start = i
                length = 0
            length += delta
        pages.append(
            separator.join(items[start:]) or "None",
        )
        try:
            page = pages[page_num - 1]
        except IndexError:
            page = pages[-1]
        return page, len(pages)

    def get_public_roles(self):
        response = self.client.get(f"{self.guild_api_url}/roles")
        all_roles = response.json()
        public_roles = []
        for role in sorted(all_roles, key=lambda x: x["position"]):
            if role["name"] == "public-roles":
                break
            if role["name"] != "@everyone":
                public_roles.append(role)

        return public_roles

    def list_commands(self):
        response = self.client.get(f"{self.guild_api_url}/commands")
        return response.json()

    def register_commands(self):
        responses = []
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
                                "type": ApplicationCommandOptionType.INTEGER.value,
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
                                "type": ApplicationCommandOptionType.ROLE.value,
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
                                "type": ApplicationCommandOptionType.ROLE.value,
                                "required": True,
                            }
                        ],
                    },
                ],
            },
        ]:
            response = self.client.post(
                f"{self.guild_api_url}/commands", json=definition
            )
            responses.append(response.json())
        return responses

    def unregister_commands(self):
        responses = []
        for command in self.list_commands():
            response = self.client.delete(
                f"{self.guild_api_url}/commands/{command['id']}"
            )
            responses.append(response)
        return responses
