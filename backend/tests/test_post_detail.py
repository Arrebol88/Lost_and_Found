from datetime import datetime, timedelta

from sqlalchemy import inspect


def test_post_likes_table_exists(client):
    from app.database import engine
    insp = inspect(engine)
    assert "post_likes" in insp.get_table_names()
    cols = {c["name"] for c in insp.get_columns("post_likes")}
    assert {"id", "post_id", "user_id", "created_at"}.issubset(cols)
    uniques = insp.get_unique_constraints("post_likes")
    assert any(set(u["column_names"]) == {"post_id", "user_id"} for u in uniques)


def test_post_comments_table_exists(client):
    from app.database import engine
    insp = inspect(engine)
    assert "post_comments" in insp.get_table_names()
    cols = {c["name"] for c in insp.get_columns("post_comments")}
    assert {"id", "post_id", "user_id", "content", "image_path", "created_at"}.issubset(cols)


def _create_post(client, headers, post_type="lost"):
    r = client.post(
        "/api/posts",
        headers=headers,
        data={
            "post_type": post_type,
            "title": "黑色雨伞",
            "category": "daily",
            "description": "长柄",
            "location": "gulou",
            "event_time": (datetime.now() - timedelta(hours=1)).isoformat(timespec="minutes"),
            "contact_type": "owner_contact" if post_type == "lost" else "self_pickup",
            "contact_detail": "微信 abc123",
        },
    )
    assert r.status_code == 201, r.text
    return r.json()


def test_get_post_detail_returns_full_fields(client, headers):
    pid = _create_post(client, headers)["id"]
    r = client.get(f"/api/posts/{pid}", headers=headers)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["id"] == pid
    assert body["contact_detail"] == "微信 abc123"
    assert body["like_count"] == 0
    assert body["liked_by_me"] is False
    assert body["author_username"] == "alice"


def test_get_post_detail_404_for_missing(client, headers):
    r = client.get("/api/posts/9999", headers=headers)
    assert r.status_code == 404


def test_get_post_detail_works_without_login(client, headers):
    pid = _create_post(client, headers)["id"]
    r = client.get(f"/api/posts/{pid}")
    assert r.status_code == 200
    assert r.json()["mine"] is False


def test_post_has_user_id_column(client):
    from app.database import engine
    cols = {c["name"] for c in inspect(engine).get_columns("posts")}
    assert "user_id" in cols
    assert "anon_id" not in cols


def test_post_detail_returns_mine_flag(client, auth):
    h_alice = auth("alice")
    h_bob = auth("bob")
    pid = _create_post(client, h_alice)["id"]
    assert client.get(f"/api/posts/{pid}", headers=h_alice).json()["mine"] is True
    assert client.get(f"/api/posts/{pid}", headers=h_bob).json()["mine"] is False
