import typing as t

import discord_interactions
import pytest

from .. import api


@pytest.fixture(autouse=True)
def disable_verification(monkeypatch):
    monkeypatch.setattr(discord_interactions, "verify_key", lambda *x, **y: True)


@pytest.fixture(autouse=True)
def configure():
    from crabot.main import app  # pylint: disable=import-outside-toplevel

    app.config.update(
        {
            "DISCORD_BOT_TOKEN": "test_bot_token",
            "DISCORD_CLIENT_ID": "test_client_id",
            "DISCORD_CLIENT_PUBLIC_KEY": "test_public_key",
        }
    )


@pytest.fixture()
def client():
    from crabot import main  # pylint: disable=import-outside-toplevel

    main.app.config["TESTING"] = True
    with main.app.test_client() as flask_client:
        yield flask_client


@pytest.fixture()
def interact(client):  # pylint: disable=redefined-outer-name
    default_interaction_type = api.Interaction.Type.APPLICATION_COMMAND

    def fnc(  # pylint: disable=too-many-arguments
        data: t.Dict[str, str],
        application_id: str = "1234567890",
        channel_id: str = "1234567890",
        guild_id: str = "1234567890",
        member_roles: t.List[str] = None,
        interaction_type: api.Interaction.Type = default_interaction_type,
    ):
        if not member_roles:
            member_roles = []
        return client.post(
            "/interactions/",
            headers={"X-Signature-Ed25519": "dummy", "X-Signature-Timestamp": "dummy"},
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
