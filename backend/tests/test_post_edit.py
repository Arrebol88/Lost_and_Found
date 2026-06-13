from datetime import datetime, timedelta
import os

ANON_A = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
ANON_B = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\xcf"
    b"\xc0\x00\x00\x00\x03\x00\x01\x5b\x6e\x40\x9b\x00\x00\x00\x00IEND\xaeB`\x82"
)


def _create(client, headers, **overrides):
    base = {
        "post_type": "lost",
        "title": "黑色雨伞",
        "category": "daily",
        "description": "长柄",
        "location": "gulou",
        "event_time": (datetime.now() - timedelta(hours=1)).isoformat(timespec="minutes"),
        "contact_type": "owner_contact",
        "contact_detail": "微信 abc123",
    }
    base.update(overrides)
    r = client.post("/api/posts", headers=headers, data=base)
    assert r.status_code == 201, r.text
    return r.json()


def _form(**overrides):
    base = {
        "title": "新标题",
        "category": "daily",
        "description": "新描述",
        "location": "xianlin",
        "event_time": (datetime.now() - timedelta(hours=2)).isoformat(timespec="minutes"),
        "contact_type": "owner_contact",
        "contact_detail": "新联系方式",
    }
    base.update(overrides)
    return base


def test_update_post_full_fields(client):
    h = {"X-Anon-Id": ANON_A}
    pid = _create(client, h)["id"]
    r = client.put(f"/api/posts/{pid}", headers=h, data=_form())
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["title"] == "新标题"
    assert body["location"] == "xianlin"
    assert body["contact_detail"] == "新联系方式"
    assert body["mine"] is True


def test_update_post_forbidden_for_other_anon(client):
    pid = _create(client, {"X-Anon-Id": ANON_A})["id"]
    r = client.put(f"/api/posts/{pid}", headers={"X-Anon-Id": ANON_B}, data=_form())
    assert r.status_code == 403


def test_update_post_404_for_missing(client):
    r = client.put("/api/posts/9999", headers={"X-Anon-Id": ANON_A}, data=_form())
    assert r.status_code == 404


def test_update_post_replace_image(client):
    h = {"X-Anon-Id": ANON_A}
    body = _create(client, h)
    pid = body["id"]
    r = client.put(
        f"/api/posts/{pid}",
        headers=h,
        data=_form(),
        files={"image": ("a.png", PNG, "image/png")},
    )
    assert r.status_code == 200, r.text
    new_path = r.json()["image_path"]
    assert new_path is not None
    assert new_path.endswith(".png")


def test_update_post_remove_image(client):
    h = {"X-Anon-Id": ANON_A}
    pid = client.post(
        "/api/posts",
        headers=h,
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
        files={"image": ("a.png", PNG, "image/png")},
    ).json()["id"]
    upload_dir = os.environ["NJU_UPLOAD_DIR"]
    detail = client.get(f"/api/posts/{pid}", headers=h).json()
    abs_p = os.path.join(upload_dir, detail["image_path"].split("uploads/", 1)[1])
    assert os.path.exists(abs_p)
    r = client.put(
        f"/api/posts/{pid}",
        headers=h,
        data={**_form(), "remove_image": "true"},
    )
    assert r.status_code == 200
    assert r.json()["image_path"] is None
    assert not os.path.exists(abs_p)


def test_update_post_rejects_post_type_change(client):
    h = {"X-Anon-Id": ANON_A}
    pid = _create(client, h)["id"]
    r = client.put(
        f"/api/posts/{pid}",
        headers=h,
        data={**_form(), "post_type": "found"},
    )
    assert r.status_code == 200
    assert r.json()["post_type"] == "lost"
