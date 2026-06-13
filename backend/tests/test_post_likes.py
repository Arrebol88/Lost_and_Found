from datetime import datetime, timedelta

ANON_A = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
ANON_B = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"


def _create_post(client):
    r = client.post("/api/posts", data={
        "post_type": "lost",
        "title": "黑色雨伞",
        "category": "daily",
        "description": "长柄",
        "location": "gulou",
        "event_time": (datetime.now() - timedelta(hours=1)).isoformat(timespec="minutes"),
        "contact_type": "owner_contact",
        "contact_detail": "微信 abc123",
    })
    assert r.status_code == 201, r.text
    return r.json()["id"]


def test_like_requires_anon_id(client):
    pid = _create_post(client)
    r = client.post(f"/api/posts/{pid}/likes")
    assert r.status_code == 400


def test_like_toggles_for_same_anon(client):
    pid = _create_post(client)
    r1 = client.post(f"/api/posts/{pid}/likes", headers={"X-Anon-Id": ANON_A})
    assert r1.status_code == 200
    assert r1.json() == {"liked": True, "like_count": 1}
    r2 = client.post(f"/api/posts/{pid}/likes", headers={"X-Anon-Id": ANON_A})
    assert r2.json() == {"liked": False, "like_count": 0}
    r3 = client.post(f"/api/posts/{pid}/likes", headers={"X-Anon-Id": ANON_A})
    assert r3.json() == {"liked": True, "like_count": 1}


def test_like_independent_per_anon(client):
    pid = _create_post(client)
    client.post(f"/api/posts/{pid}/likes", headers={"X-Anon-Id": ANON_A})
    r = client.post(f"/api/posts/{pid}/likes", headers={"X-Anon-Id": ANON_B})
    assert r.json() == {"liked": True, "like_count": 2}


def test_like_post_not_found(client):
    r = client.post("/api/posts/9999/likes", headers={"X-Anon-Id": ANON_A})
    assert r.status_code == 404
