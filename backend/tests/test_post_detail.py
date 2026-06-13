from datetime import datetime, timedelta

from sqlalchemy import inspect


def test_post_likes_table_exists(client):
    from app.database import engine
    insp = inspect(engine)
    assert "post_likes" in insp.get_table_names()
    cols = {c["name"] for c in insp.get_columns("post_likes")}
    assert {"id", "post_id", "anon_id", "created_at"}.issubset(cols)
    uniques = insp.get_unique_constraints("post_likes")
    assert any(set(u["column_names"]) == {"post_id", "anon_id"} for u in uniques)


def test_post_comments_table_exists(client):
    from app.database import engine
    insp = inspect(engine)
    assert "post_comments" in insp.get_table_names()
    cols = {c["name"] for c in insp.get_columns("post_comments")}
    assert {"id", "post_id", "anon_id", "content", "image_path", "created_at"}.issubset(cols)


ANON = "11111111-1111-1111-1111-111111111111"


def _create_post(client, post_type="lost"):
    r = client.post("/api/posts", data={
        "post_type": post_type,
        "title": "黑色雨伞",
        "category": "daily",
        "description": "长柄",
        "location": "gulou",
        "event_time": (datetime.now() - timedelta(hours=1)).isoformat(timespec="minutes"),
        "contact_type": "owner_contact" if post_type == "lost" else "self_pickup",
        "contact_detail": "微信 abc123",
    })
    assert r.status_code == 201, r.text
    return r.json()


def test_get_post_detail_returns_full_fields(client):
    pid = _create_post(client)["id"]
    r = client.get(f"/api/posts/{pid}", headers={"X-Anon-Id": ANON})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["id"] == pid
    assert body["contact_detail"] == "微信 abc123"
    assert body["like_count"] == 0
    assert body["liked_by_me"] is False


def test_get_post_detail_404_for_missing(client):
    r = client.get("/api/posts/9999", headers={"X-Anon-Id": ANON})
    assert r.status_code == 404


def test_get_post_detail_requires_anon_id(client):
    pid = _create_post(client)["id"]
    r = client.get(f"/api/posts/{pid}")
    assert r.status_code == 400
