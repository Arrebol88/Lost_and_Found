from datetime import datetime, timedelta
import os

ANON_A = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
ANON_B = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\xcf"
    b"\xc0\x00\x00\x00\x03\x00\x01\x5b\x6e\x40\x9b\x00\x00\x00\x00IEND\xaeB`\x82"
)


def _create(client, headers, with_image=False):
    data = {
        "post_type": "lost",
        "title": "黑色雨伞",
        "category": "daily",
        "description": "长柄",
        "location": "gulou",
        "event_time": (datetime.now() - timedelta(hours=1)).isoformat(timespec="minutes"),
        "contact_type": "owner_contact",
        "contact_detail": "微信 abc123",
    }
    files = {"image": ("a.png", PNG, "image/png")} if with_image else None
    r = client.post("/api/posts", headers=headers, data=data, files=files)
    assert r.status_code == 201, r.text
    return r.json()


def test_delete_post_forbidden_for_other_anon(client):
    pid = _create(client, {"X-Anon-Id": ANON_A})["id"]
    r = client.delete(f"/api/posts/{pid}", headers={"X-Anon-Id": ANON_B})
    assert r.status_code == 403


def test_delete_post_404(client):
    r = client.delete("/api/posts/9999", headers={"X-Anon-Id": ANON_A})
    assert r.status_code == 404


def test_delete_post_cascades(client):
    h = {"X-Anon-Id": ANON_A}
    body = _create(client, h, with_image=True)
    pid = body["id"]
    image_rel = body["image_path"]

    client.post(f"/api/posts/{pid}/likes", headers={"X-Anon-Id": ANON_B})
    cmt = client.post(
        f"/api/posts/{pid}/comments",
        headers=h,
        data={"content": "我也见过"},
        files={"image": ("c.png", PNG, "image/png")},
    ).json()
    upload_dir = os.environ["NJU_UPLOAD_DIR"]
    main_image = os.path.join(upload_dir, image_rel.split("uploads/", 1)[1])
    cmt_image = os.path.join(upload_dir, cmt["image_path"].split("uploads/", 1)[1])
    assert os.path.exists(main_image)
    assert os.path.exists(cmt_image)

    r = client.delete(f"/api/posts/{pid}", headers=h)
    assert r.status_code == 204

    r2 = client.get(f"/api/posts/{pid}", headers=h)
    assert r2.status_code == 404
    r3 = client.get(f"/api/posts/{pid}/comments", headers=h)
    assert r3.status_code == 404
    assert not os.path.exists(main_image)
    assert not os.path.exists(cmt_image)
