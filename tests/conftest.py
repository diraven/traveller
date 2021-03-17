import functools

import pytest


@pytest.fixture()
def client():
    from crabot import main

    main.app.config["TESTING"] = True
    with main.app.test_client() as client:
        yield client


def verify_key_decorator(*args, **kwargs):
    def _decorator(fnc):
        return fnc

    return _decorator


@pytest.fixture(autouse=True)
def patch_signature(monkeypatch):
    monkeypatch.setattr(
        "discord_interactions.verify_key_decorator", verify_key_decorator
    )
