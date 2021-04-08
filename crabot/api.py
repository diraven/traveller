import os
import typing as t

import flask
import requests
from cached_property import cached_property_with_ttl
from requests.sessions import CaseInsensitiveDict

from .models import ApplicationCommandOptionType, Color, Interaction, Member, Role


class Api:
    def __init__(self, guild_id: str, bot_token: str, version="8"):
        self.base_api_url = "https://discord.com/api"

        self.application_id = os.environ["DISCORD_CLIENT_ID"]

        self.version = version
        self.guild_id = guild_id
        self.bot_token = bot_token

        self.api_url = f"{self.base_api_url}/v{self.version}"
        self.guild_api_url = f"{self.api_url}/guilds/{guild_id}"

        self.client = requests.session()
        self.client.headers = CaseInsensitiveDict(
            {"Authorization": f"Bot {self.bot_token}"}
        )

    def _list_commands(self):
        response = self.client.get(f"{self.guild_api_url}/commands")
        return response.json()

    def _register_commands(self):
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
                    {
                        "name": "play",
                        "description": "Хто грає?",
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
                f"{self.api_url}/applications/{self.application_id}"
                f"/guilds/{self.guild_id}/commands",
                json=definition,
            )
            response.raise_for_status()
        return responses

    def _unregister_commands(self):
        responses = []
        for command in self._list_commands():
            response = self.client.delete(
                f"{self.guild_api_url}/commands/{command['id']}"
            )
            responses.append(response)
        return responses

    @staticmethod
    def _new_interaction_response(
        text: str, title: str = "", footer: str = "", color=Color.DEFAULT
    ):
        return flask.jsonify(
            {
                "type": Interaction.ResponseType.CHANNEL_MESSAGE_WITH_SOURCE.value,
                "data": {
                    "embeds": [
                        {
                            "description": text,
                            "title": title,
                            "footer": {
                                "text": footer,
                                "icon_url": "",
                                "proxy_icon_url": "",
                            },
                            "color": color.value,
                            # "type": "rich",
                            # "": "",
                            # "timestamp": "",
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
                    ],
                },
            }
        )

    @staticmethod
    def success(text: str, title: str = "", footer: str = ""):
        if not title:
            title = "Успіх"
        return Api._new_interaction_response(text, title, footer, Color.GREEN)

    @staticmethod
    def info(text: str, title: str = "", footer: str = ""):
        if not title:
            title = "Інформація"
        return Api._new_interaction_response(text, title, footer, Color.BLUE)

    @staticmethod
    def warning(text: str, title: str = "", footer: str = ""):
        if not title:
            title = "Попередження"
        return Api._new_interaction_response(text, title, footer, Color.ORANGE)

    @staticmethod
    def error(text: str, title: str = "", footer: str = ""):
        if not title:
            title = "Помилка"
        return Api._new_interaction_response(text, title, footer, Color.RED)

    @staticmethod
    def get_page(items: t.Iterable[str], page_num: int = 1) -> t.Tuple[str, int]:
        items = list(items)
        separator = " **|** "
        max_page_len = 1000
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
            separator.join(items[start:]) or "",
        )
        try:
            page = pages[page_num - 1]
        except IndexError:
            page = pages[-1]
        return page, len(pages)

    @staticmethod
    def parse_interaction(data: t.Dict) -> Interaction:
        return Interaction(**data)

    @cached_property_with_ttl(ttl=5)
    def guild_roles(self) -> t.List[Role]:
        response = self.client.get(f"{self.guild_api_url}/roles")
        response.raise_for_status()
        return [Role(**data) for data in response.json()]

    @property
    def public_roles(self) -> t.List[Role]:
        public_roles = []
        for role in sorted(self.guild_roles, key=lambda x: x.position):
            if role.name == "public-roles":
                break
            if role.name != "@everyone":
                public_roles.append(role)

        return public_roles

    def member_add_role(self, member: Member, role: Role) -> None:
        response = self.client.put(
            f"{self.guild_api_url}/members/{member.user.id}/roles/{role.id}"
        )
        response.raise_for_status()

    def member_remove_role(self, member: Member, role: Role) -> None:
        response = self.client.delete(
            f"{self.guild_api_url}/members/{member.user.id}/roles/{role.id}"
        )
        response.raise_for_status()

    @cached_property_with_ttl(ttl=60)
    def guild_members(self) -> t.List[Member]:
        has_more = True
        members = []
        after = ""
        while has_more:
            response = self.client.get(
                f"{self.guild_api_url}/members?limit=1000{after}",
            )
            response.raise_for_status()
            members += [Member(**data) for data in response.json()]
            has_more = len(response.json()) > 0
            if has_more:
                after = f"&after={members[-1].user.id}"
        return members

    def get_role(self, role_id: str) -> Role:
        return next(filter(lambda role: role.id == role_id, self.guild_roles))

    def get_public_role(self, role_id: str) -> Role:
        return next(filter(lambda role: role.id == role_id, self.public_roles))
