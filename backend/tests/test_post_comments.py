from datetime import datetime, timedelta
import os

PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\xcf"
    b"\xc0\x00\x00\x00\x03\x00\x01\x5b\x6e\x40\x9b\x00\x00\x00\x00IEND\xaeB`\x82"
)


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


def test_create_comment_text_only(client, headers):
    pid = _create_post(client, headers)
    r = client.post(
        f"/api/posts/{pid}/comments",
        headers=headers,
        data={"content": "我也见过"},
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["content"] == "我也见过"
    assert body["image_path"] is None
    assert body["mine"] is True
    assert body["author_username"] == "alice"


def test_create_comment_rejects_empty_content(client, headers):
    pid = _create_post(client, headers)
    r = client.post(
        f"/api/posts/{pid}/comments",
        headers=headers,
        data={"content": "  "},
    )
    assert r.status_code == 400


def test_create_comment_with_image(client, headers):
    pid = _create_post(client, headers)
    r = client.post(
        f"/api/posts/{pid}/comments",
        headers=headers,
        data={"content": "看图"},
        files={"image": ("a.png", PNG, "image/png")},
    )
    assert r.status_code == 201, r.text
    assert r.json()["image_path"].endswith(".png")


def test_list_comments_sorted_desc_with_mine_flag(client, auth):
    h_alice = auth("alice")
    h_bob = auth("bob")
    pid = _create_post(client, h_alice)
    client.post(f"/api/posts/{pid}/comments", headers=h_alice, data={"content": "first"})
    client.post(f"/api/posts/{pid}/comments", headers=h_bob, data={"content": "second"})
    r = client.get(f"/api/posts/{pid}/comments", headers=h_alice)
    assert r.status_code == 200
    items = r.json()
    assert [c["content"] for c in items] == ["second", "first"]
    mine_map = {c["content"]: c["mine"] for c in items}
    assert mine_map == {"first": True, "second": False}


def test_delete_comment_only_by_author(client, auth):
    h_alice = auth("alice")
    h_bob = auth("bob")
    pid = _create_post(client, h_alice)
    cid = client.post(
        f"/api/posts/{pid}/comments",
        headers=h_alice,
        data={"content": "x"},
    ).json()["id"]
    r = client.delete(f"/api/comments/{cid}", headers=h_bob)
    assert r.status_code == 403
    r2 = client.delete(f"/api/comments/{cid}", headers=h_alice)
    assert r2.status_code == 204


def test_delete_comment_removes_image_file(client, headers):
    pid = _create_post(client, headers)
    body = client.post(
        f"/api/posts/{pid}/comments",
        headers=headers,
        data={"content": "img"},
        files={"image": ("a.png", PNG, "image/png")},
    ).json()
    rel = body["image_path"]
    upload_dir = os.environ["NJU_UPLOAD_DIR"]
    abs_p = os.path.join(upload_dir, rel.split("uploads/", 1)[1])
    assert os.path.exists(abs_p)
    r = client.delete(f"/api/comments/{body['id']}", headers=headers)
    assert r.status_code == 204
    assert not os.path.exists(abs_p)


def test_create_comment_requires_login(client, headers):
    pid = _create_post(client, headers)
    r = client.post(f"/api/posts/{pid}/comments", data={"content": "x"})
    assert r.status_code == 401
