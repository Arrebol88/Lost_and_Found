import os
import uuid
from datetime import datetime
from pathlib import Path

MAX_BYTES = 5 * 1024 * 1024
ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp"}
EXT_BY_MIME = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}

SIGNATURES = {
    "image/jpeg": [b"\xff\xd8\xff"],
    "image/png": [b"\x89PNG\r\n\x1a\n"],
    "image/webp": [b"RIFF"],
}


class InvalidImageError(ValueError):
    pass


class ImageTooLargeError(ValueError):
    pass


def _upload_root() -> Path:
    return Path(os.getenv("NJU_UPLOAD_DIR", "./uploads"))


def _check_signature(content: bytes, content_type: str) -> bool:
    if content_type not in SIGNATURES:
        return False
    if not any(content.startswith(sig) for sig in SIGNATURES[content_type]):
        return False
    if content_type == "image/webp":
        if len(content) < 12 or content[8:12] != b"WEBP":
            return False
    return True


def save_image(*, filename: str, content: bytes, content_type: str) -> str:
    if content_type not in ALLOWED_MIME:
        raise InvalidImageError(f"不支持的图片类型：{content_type}")
    if len(content) > MAX_BYTES:
        raise ImageTooLargeError("图片超过 5MB 限制")
    if not _check_signature(content, content_type):
        raise InvalidImageError("图片内容与扩展名不匹配")

    now = datetime.now()
    sub = Path(f"{now.year:04d}/{now.month:02d}/{now.day:02d}")
    target_dir = _upload_root() / sub
    target_dir.mkdir(parents=True, exist_ok=True)
    name = f"{uuid.uuid4().hex}{EXT_BY_MIME[content_type]}"
    abs_path = target_dir / name
    abs_path.write_bytes(content)
    return f"uploads/{sub.as_posix()}/{name}"


def delete_image(rel_path: str) -> None:
    if not rel_path or not rel_path.startswith("uploads/"):
        return
    abs_path = _upload_root() / rel_path.split("uploads/", 1)[1]
    try:
        abs_path.unlink(missing_ok=True)
    except OSError:
        pass
