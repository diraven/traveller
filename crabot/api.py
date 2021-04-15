import os
import time
import typing as t
from datetime import datetime, timedelta
from functools import lru_cache, wraps

import flask
import requests
from requests.sessions import CaseInsensitiveDict

from .models import ApplicationCommandOptionType, Color, Interaction, Member, Role


def timed_lru_cache(seconds: int):
    def wrapper_cache(func):
        func = lru_cache()(func)
        func.lifetime = timedelta(seconds=seconds)
        func.expiration = datetime.utcnow() + func.lifetime

        @wraps(func)
        def wrapped_func(*args, **kwargs):
            if datetime.utcnow() >= func.expiration:
                func.cache_clear()
                func.expiration = datetime.utcnow() + func.lifetime

            return func(*args, **kwargs)

        return wrapped_func

    return wrapper_cache


class Api:
    def __init__(self, bot_token: str, version="8"):
        self.base_api_url = "https://discord.com/api"

        self.application_id = os.environ["DISCORD_CLIENT_ID"]

        self.version = version
        self.bot_token = bot_token

        self.api_url = f"{self.base_api_url}/v{self.version}"

        self.client = requests.session()
        self.client.headers = CaseInsensitiveDict(
            {"Authorization": f"Bot {self.bot_token}"}
        )

    def _list_commands(self, guild_id: str):
        response = self.client.get(f"{self.api_url}/guilds/{guild_id}/commands")
        return response.json()

    def _register_commands(self, guild_id: str):
        responses: t.List[requests.Response] = []
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
                    {
                        "name": "my",
                        "description": "Мої ігри",
                        "type": 1,
                        "options": [],
                    },
                ],
            },
        ]:
            response = self.client.post(
                f"{self.api_url}/applications/{self.application_id}"
                f"/guilds/{guild_id}/commands",
                json=definition,
            )
            response.raise_for_status()
        return responses

    def _unregister_commands(self, guild_id: str):
        responses = []
        for command in self._list_commands(guild_id):
            response = self.client.delete(
                f"{self.api_url}/guilds/{guild_id}/commands/{command['id']}"
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

    @timed_lru_cache(60)
    def get_guild_roles(self, guild_id: str) -> t.List[Role]:
        response = self.client.get(f"{self.api_url}/guilds/{guild_id}/roles")
        response.raise_for_status()
        return [Role(**data) for data in response.json()]

    @timed_lru_cache(60)
    def get_public_roles(self, guild_id: str) -> t.List[Role]:
        public_roles = []
        for role in sorted(self.get_guild_roles(guild_id), key=lambda x: x.position):
            if role.name == "public-roles":
                break
            if role.name != "@everyone":
                public_roles.append(role)

        return public_roles

    def member_add_role(self, guild_id: str, member: Member, role: Role) -> None:
        response = self.client.put(
            f"{self.api_url}/guilds/{guild_id}/members/{member.user.id}/roles/{role.id}"
        )
        response.raise_for_status()

    def member_remove_role(self, guild_id: str, member: Member, role: Role) -> None:
        response = self.client.delete(
            f"{self.api_url}/guilds/{guild_id}/members/{member.user.id}/roles/{role.id}"
        )
        response.raise_for_status()

    # @timed_lru_cache(1 * 60 * 60 * 24)
    def get_guild_members(self, guild_id) -> t.List[Member]:
        has_more = True
        members = []
        after = ""
        while has_more:
            response = self.client.get(
                f"{self.api_url}/guilds/{guild_id}/members?limit=1000{after}",
            )
            response.raise_for_status()
            members += [Member(**data) for data in response.json()]
            has_more = len(response.json()) > 0
            if has_more:
                after = f"&after={members[-1].user.id}"
                if int(response.headers["x-ratelimit-remaining"]) == 0:
                    time.sleep(
                        float(response.headers["x-ratelimit-reset"]) - time.time()
                    )
        return members

    def get_member(self, guild_id: str, user_id) -> Member:
        response = self.client.get(
            f"{self.api_url}/guilds/{guild_id}/members/{user_id}",
        )
        response.raise_for_status()
        return Member(**response.json())

    def get_role(self, guild_id: str, role_id: str) -> Role:
        return next(
            filter(lambda role: role.id == role_id, self.get_guild_roles(guild_id))
        )

    def get_public_role(self, guild_id: str, role_id: str) -> Role:
        return next(
            filter(lambda role: role.id == role_id, self.get_public_roles(guild_id))
        )
