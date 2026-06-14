from datetime import datetime, timedelta


def _form(**overrides):
    base = {
        "post_type": "lost",
        "title": "黑色耳机",
        "category": "electronics",
        "description": "降噪耳机",
        "location": "xianlin",
        "event_time": (datetime.now() - timedelta(hours=2)).isoformat(timespec="minutes"),
        "contact_type": "owner_contact",
        "contact_detail": "微信 abc123",
    }
    base.update(overrides)
    return base


def _create(client, headers, **overrides):
    r = client.post("/api/posts", headers=headers, data=_form(**overrides))
    assert r.status_code == 201, r.text
    return r.json()


def test_list_posts_without_filters_returns_all(client, headers):
    _create(client, headers, post_type="lost", contact_type="owner_contact", title="A")
    _create(client, headers, post_type="found", contact_type="self_pickup", title="B")
    r = client.get("/api/posts")
    assert r.status_code == 200
    assert sorted(p["title"] for p in r.json()) == ["A", "B"]


def test_list_posts_filters_by_post_type(client, headers):
    _create(client, headers, post_type="lost", contact_type="owner_contact", title="寻物耳机")
    _create(client, headers, post_type="found", contact_type="self_pickup", title="寻主雨伞")
    r = client.get("/api/posts", params={"post_type": "lost"})
    assert r.status_code == 200, r.text
    titles = [p["title"] for p in r.json()]
    assert titles == ["寻物耳机"]


def test_list_posts_filters_by_category(client, headers):
    _create(client, headers, title="耳机", category="electronics")
    _create(client, headers, title="校园卡", category="id_card")
    r = client.get("/api/posts", params={"post_type": "lost", "category": "id_card"})
    assert [p["title"] for p in r.json()] == ["校园卡"]


def test_list_posts_filters_by_location(client, headers):
    _create(client, headers, title="仙林耳机", location="xianlin")
    _create(client, headers, title="鼓楼耳机", location="gulou")
    r = client.get("/api/posts", params={"post_type": "lost", "location": "gulou"})
    assert [p["title"] for p in r.json()] == ["鼓楼耳机"]


def test_list_posts_filters_by_time_range(client, headers):
    _create(client, headers, title="近期", event_time=(datetime.now() - timedelta(hours=3)).isoformat(timespec="minutes"))
    _create(client, headers, title="较早", event_time=(datetime.now() - timedelta(days=8)).isoformat(timespec="minutes"))
    r = client.get("/api/posts", params={"post_type": "lost", "time_range": "older_than_7d"})
    assert [p["title"] for p in r.json()] == ["较早"]


def test_list_posts_excludes_contact_detail(client, headers):
    _create(client, headers)
    r = client.get("/api/posts", params={"post_type": "lost"})
    body = r.json()[0]
    assert "contact_detail" not in body
    assert "contact_type" not in body
    assert "description" not in body


def test_list_posts_limit_max_100(client):
    r = client.get("/api/posts", params={"post_type": "lost", "limit": 101})
    assert r.status_code == 422


def test_list_posts_mine_requires_login(client):
    r = client.get("/api/posts", params={"mine": "true"})
    assert r.status_code == 401


def test_list_posts_mine_filters_by_user(client, auth):
    h_alice = auth("alice")
    h_bob = auth("bob")
    client.post("/api/posts", headers=h_alice, data=_form(title="alice-1"))
    client.post("/api/posts", headers=h_bob, data=_form(title="bob-1"))
    r = client.get("/api/posts", params={"mine": "true"}, headers=h_alice)
    assert r.status_code == 200
    titles = [p["title"] for p in r.json()]
    assert titles == ["alice-1"]


def test_list_posts_includes_author_username(client, headers):
    _create(client, headers, title="who am i")
    r = client.get("/api/posts", params={"post_type": "lost"})
    item = next(p for p in r.json() if p["title"] == "who am i")
    assert item["author_username"] == "alice"
