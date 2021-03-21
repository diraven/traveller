import typing as t

import pytest


@pytest.fixture(autouse=True)
def patch_signature(monkeypatch):
    def verify_key_decorator(*args, **kwargs):  # pylint: disable=unused-argument
        def _decorator(fnc):
            return fnc

        return _decorator

    monkeypatch.setattr(
        "discord_interactions.verify_key_decorator", verify_key_decorator
    )


@pytest.fixture(autouse=True)
def configure():
    from crabot.main import app  # pylint: disable=import-outside-toplevel

    app.config.update(
        {
            "DISCORD_BOT_TOKEN": "test_bot_token",
            "DISCORD_CLIENT_ID": "test_client_id",
            "DISCORD_CLIENT_PUBLIC_KEY": "test_public_key",
            "DISCORD_GUILD_ID": "test_guild_id",
        }
    )


@pytest.fixture(scope="session")
def client():
    from crabot import main  # pylint: disable=import-outside-toplevel

    main.app.config["TESTING"] = True
    with main.app.test_client() as flask_client:
        yield flask_client


@pytest.fixture(scope="session")
def interact(client):  # pylint: disable=redefined-outer-name
    from crabot import discord  # pylint: disable=import-outside-toplevel

    default_interaction_type = discord.InteractionType.APPLICATION_COMMAND

    def fnc(  # pylint: disable=too-many-arguments
        data: t.Dict[str, str],
        application_id: str = "1234567890",
        channel_id: str = "1234567890",
        guild_id: str = "1234567890",
        member_roles: t.List[str] = None,
        interaction_type: discord.InteractionType = default_interaction_type,
    ):
        if not member_roles:
            member_roles = []
        return client.post(
            "/interactions/",
            json={
                "application_id": application_id,
                "channel_id": channel_id,
                "data": data,
                "guild_id": guild_id,
                "id": "1234567890",
                "member": {
                    "deaf": False,
                    "is_pending": False,
                    "joined_at": "2020-01-20T14:56:10.619000+00:00",
                    "mute": False,
                    "nick": None,
                    "pending": False,
                    "permissions": "8589934591",
                    "premium_since": None,
                    "roles": member_roles,
                    "user": {
                        "avatar": "1234567890",
                        "discriminator": "1234",
                        "id": "1234567890",
                        "public_flags": 256,
                        "username": "TestUser",
                    },
                },
                "token": "TestToken",
                "type": interaction_type.value,
                "version": 1,
            },
        )

    return fnc
