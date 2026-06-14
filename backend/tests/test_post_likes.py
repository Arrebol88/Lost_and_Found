from datetime import datetime, timedelta


def _create_post(client, headers):
    r = client.post(
        "/api/posts",
        headers=headers,
        data={
            "post_type": "lost",
            "title": "黑色雨伞",
            "category": "daily",
            "description": "长柄",
            "location": "gulou",
            "event_time": (datetime.now() - timedelta(hours=1)).isoformat(timespec="minutes"),
            "contact_type": "owner_contact",
            "contact_detail": "微信 abc123",
        },
    )
    assert r.status_code == 201, r.text
    return r.json()["id"]


def test_like_requires_login(client, headers):
    pid = _create_post(client, headers)
    r = client.post(f"/api/posts/{pid}/likes")
    assert r.status_code == 401


def test_like_toggles_for_same_user(client, headers):
    pid = _create_post(client, headers)
    r1 = client.post(f"/api/posts/{pid}/likes", headers=headers)
    assert r1.status_code == 200
    assert r1.json() == {"liked": True, "like_count": 1}
    r2 = client.post(f"/api/posts/{pid}/likes", headers=headers)
    assert r2.json() == {"liked": False, "like_count": 0}
    r3 = client.post(f"/api/posts/{pid}/likes", headers=headers)
    assert r3.json() == {"liked": True, "like_count": 1}


def test_like_independent_per_user(client, auth):
    h_alice = auth("alice")
    h_bob = auth("bob")
    pid = _create_post(client, h_alice)
    client.post(f"/api/posts/{pid}/likes", headers=h_alice)
    r = client.post(f"/api/posts/{pid}/likes", headers=h_bob)
    assert r.json() == {"liked": True, "like_count": 2}


def test_like_post_not_found(client, headers):
    r = client.post("/api/posts/9999/likes", headers=headers)
    assert r.status_code == 404
