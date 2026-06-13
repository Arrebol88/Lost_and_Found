from datetime import datetime, timedelta
import pytest
from pydantic import ValidationError


def _payload(**overrides):
    base = dict(
        post_type="found",
        title="黑色雨伞",
        category="daily",
        description=None,
        location="逸夫楼 B201",
        event_time=datetime.now() - timedelta(hours=1),
        contact_type="self_pickup",
        contact_detail="工作日 8-17 自取",
    )
    base.update(overrides)
    return base


def test_valid_found_post():
    from app.schemas import PostCreate
    PostCreate(**_payload())


def test_valid_lost_post():
    from app.schemas import PostCreate
    PostCreate(**_payload(post_type="lost", contact_type="owner_contact",
                          contact_detail="微信 abc123"))


def test_lost_must_use_owner_contact():
    from app.schemas import PostCreate
    with pytest.raises(ValidationError):
        PostCreate(**_payload(post_type="lost", contact_type="self_pickup"))


def test_found_cannot_use_owner_contact():
    from app.schemas import PostCreate
    with pytest.raises(ValidationError):
        PostCreate(**_payload(contact_type="owner_contact"))


def test_event_time_in_future_rejected():
    from app.schemas import PostCreate
    with pytest.raises(ValidationError):
        PostCreate(**_payload(event_time=datetime.now() + timedelta(hours=1)))


def test_event_time_too_old_rejected():
    from app.schemas import PostCreate
    with pytest.raises(ValidationError):
        PostCreate(**_payload(event_time=datetime.now() - timedelta(days=400)))


def test_title_too_long_rejected():
    from app.schemas import PostCreate
    with pytest.raises(ValidationError):
        PostCreate(**_payload(title="x" * 51))


def test_invalid_category_rejected():
    from app.schemas import PostCreate
    with pytest.raises(ValidationError):
        PostCreate(**_payload(category="not_a_category"))
