from .. import api


def test_wrong_http_term(client):
    resp = client.get("/interactions/")
    assert resp.status_code == 405


def test_ping(interact):
    resp = interact({}, interaction_type=api.Interaction.Type.PING)
    assert resp.status_code == 200
    assert resp.json["type"] == 1


def test_interaction(interact):
    resp = interact({"id": "822467551577243709", "name": "ping"})
    assert resp.status_code == 200
