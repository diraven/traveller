import json


def test_wrong_http_term(client):
    resp = client.get("/interactions/")
    assert resp.status_code == 405


def test_interaction(client):
    resp = client.post(
        "/interactions/",
        json={
            "type": 2,
            "token": "A_UNIQUE_TOKEN",
            "member": {
                "user": {
                    "id": 53908232506183680,
                    "username": "Mason",
                    "avatar": "a_d5efa99b3eeaa7dd43acca82f5692432",
                    "discriminator": "1337",
                    "public_flags": 131141,
                },
                "roles": ["539082325061836999"],
                "premium_since": None,
                "permissions": "2147483647",
                "pending": False,
                "nick": None,
                "mute": False,
                "joined_at": "2017-03-13T19:19:14.040000+00:00",
                "is_pending": False,
                "deaf": False,
            },
            "id": "786008729715212338",
            "guild_id": "290926798626357999",
            "data": {
                "options": [{"name": "cardname", "value": "The Gitrog Monster"}],
                "name": "cardsearch",
                "id": "771825006014889984",
            },
            "channel_id": "645027906669510667",
        },
    )
    assert resp.status_code == 200
