from datetime import datetime, timedelta
import os


def _form(**overrides):
    base = {
        "post_type": "found",
        "title": "黑色雨伞",
        "category": "daily",
        "description": "长柄",
        "location": "gulou",
        "event_time": (datetime.now() - timedelta(hours=1)).isoformat(timespec="minutes"),
        "contact_type": "self_pickup",
        "contact_detail": "工作日 8-17 自取",
    }
    base.update(overrides)
    return base


def test_create_lost_post_no_image(client):
    r = client.post("/api/posts", data=_form(
        post_type="lost", contact_type="owner_contact", contact_detail="微信 abc123"))
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["id"] >= 1
    assert body["post_type"] == "lost"
    assert body["image_path"] is None


def test_create_found_post_with_png(client):
    PNG = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\xcf"
        b"\xc0\x00\x00\x00\x03\x00\x01\x5b\x6e\x40\x9b\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    r = client.post(
        "/api/posts",
        data=_form(),
        files={"image": ("a.png", PNG, "image/png")},
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["image_path"].startswith("uploads/")
    assert body["image_path"].endswith(".png")
    upload_dir = os.environ["NJU_UPLOAD_DIR"]
    abs_p = os.path.join(upload_dir, body["image_path"].split("uploads/", 1)[1])
    assert os.path.exists(abs_p)


def test_create_post_rejects_free_text_location(client):
    r = client.post("/api/posts", data=_form(location="逸夫楼 B201"))
    assert r.status_code == 400
    assert "location" in r.json()["detail"]


def test_create_post_accepts_campus_location(client):
    r = client.post("/api/posts", data=_form(location="xianlin"))
    assert r.status_code == 201, r.text
    assert r.json()["location"] == "xianlin"
