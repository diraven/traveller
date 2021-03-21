def test_wrong_http_term(client):
    resp = client.get("/interactions/")
    assert resp.status_code == 405


def test_interaction(interact):
    resp = interact(data={"id": "822467551577243709", "name": "ping"})
    assert resp.status_code == 200
