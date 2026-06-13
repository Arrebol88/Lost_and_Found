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
