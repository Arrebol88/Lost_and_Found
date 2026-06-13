import pytest

PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\xcf"
    b"\xc0\x00\x00\x00\x03\x00\x01\x5b\x6e\x40\x9b\x00\x00\x00\x00IEND\xaeB`\x82"
)


def test_save_valid_png(tmp_path, monkeypatch):
    monkeypatch.setenv("NJU_UPLOAD_DIR", str(tmp_path))
    from app.storage import save_image
    rel = save_image(filename="a.png", content=PNG_BYTES, content_type="image/png")
    assert rel.startswith("uploads/")
    assert rel.endswith(".png")
    abs_path = tmp_path / rel.split("uploads/", 1)[1]
    assert abs_path.exists()
    assert abs_path.read_bytes() == PNG_BYTES


def test_reject_oversize(tmp_path, monkeypatch):
    monkeypatch.setenv("NJU_UPLOAD_DIR", str(tmp_path))
    from app.storage import save_image, ImageTooLargeError
    big = b"\x89PNG\r\n\x1a\n" + b"\x00" * (5 * 1024 * 1024 + 1)
    with pytest.raises(ImageTooLargeError):
        save_image(filename="big.png", content=big, content_type="image/png")


def test_reject_fake_extension(tmp_path, monkeypatch):
    monkeypatch.setenv("NJU_UPLOAD_DIR", str(tmp_path))
    from app.storage import save_image, InvalidImageError
    fake = b"MZ\x90\x00" + b"\x00" * 100
    with pytest.raises(InvalidImageError):
        save_image(filename="evil.jpg", content=fake, content_type="image/jpeg")


def test_reject_unsupported_mime(tmp_path, monkeypatch):
    monkeypatch.setenv("NJU_UPLOAD_DIR", str(tmp_path))
    from app.storage import save_image, InvalidImageError
    with pytest.raises(InvalidImageError):
        save_image(filename="a.gif", content=b"GIF89a", content_type="image/gif")


# ---- API 级错误分支与边界（任务 8）----

from datetime import datetime, timedelta


def _api_form(**overrides):
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


def test_api_reject_lost_with_self_pickup(client):
    r = client.post("/api/posts", data=_api_form(post_type="lost"))
    assert r.status_code == 400


def test_api_reject_invalid_category(client):
    r = client.post("/api/posts", data=_api_form(category="not_a_category"))
    assert r.status_code == 400


def test_api_reject_event_time_in_future(client):
    future = (datetime.now() + timedelta(hours=1)).isoformat(timespec="minutes")
    r = client.post("/api/posts", data=_api_form(event_time=future))
    assert r.status_code == 400


def test_api_reject_oversize_image(client):
    big = b"\x89PNG\r\n\x1a\n" + b"\x00" * (5 * 1024 * 1024 + 1)
    r = client.post("/api/posts", data=_api_form(),
                    files={"image": ("big.png", big, "image/png")})
    assert r.status_code == 413


def test_api_reject_fake_image(client):
    fake = b"MZ\x90\x00" + b"\x00" * 100
    r = client.post("/api/posts", data=_api_form(),
                    files={"image": ("a.jpg", fake, "image/jpeg")})
    assert r.status_code == 400


def test_api_reject_title_51_chars(client):
    r = client.post("/api/posts", data=_api_form(title="x" * 51))
    assert r.status_code == 400
