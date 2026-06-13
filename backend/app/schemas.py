from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator


class PostType(str, Enum):
    found = "found"
    lost = "lost"


class Category(str, Enum):
    electronics = "electronics"
    id_card = "id_card"
    bag = "bag"
    accessory = "accessory"
    clothing = "clothing"
    daily = "daily"
    study = "study"
    sports = "sports"
    personal_care = "personal_care"


class CampusLocation(str, Enum):
    gulou = "gulou"
    xianlin = "xianlin"
    suzhou = "suzhou"
    pukou = "pukou"


class TimeRange(str, Enum):
    within_1d = "within_1d"
    within_3d = "within_3d"
    within_7d = "within_7d"
    older_than_7d = "older_than_7d"


class ContactType(str, Enum):
    self_pickup = "self_pickup"
    contact = "contact"
    handed_over = "handed_over"
    owner_contact = "owner_contact"


class PostCreate(BaseModel):
    post_type: PostType
    title: str = Field(..., min_length=1, max_length=50)
    category: Category
    description: Optional[str] = Field(None, max_length=500)
    location: CampusLocation
    event_time: datetime
    contact_type: ContactType
    contact_detail: str = Field(..., min_length=1, max_length=200)

    @field_validator("event_time")
    @classmethod
    def _time_in_range(cls, v: datetime) -> datetime:
        now = datetime.now()
        if v > now:
            raise ValueError("丢失/捡到时间不能晚于当前时间")
        if v < now - timedelta(days=365):
            raise ValueError("丢失/捡到时间不能早于一年前")
        return v

    @model_validator(mode="after")
    def _contact_match_post_type(self):
        if self.post_type == PostType.lost and self.contact_type != ContactType.owner_contact:
            raise ValueError("寻物帖的联系方式类型必须是 owner_contact")
        if self.post_type == PostType.found and self.contact_type == ContactType.owner_contact:
            raise ValueError("寻主帖的联系方式类型必须是 自取/联系方式/已移交管理处")
        return self


class PostOut(BaseModel):
    id: int
    post_type: PostType
    title: str
    category: Category
    image_path: Optional[str]
    description: Optional[str]
    location: CampusLocation
    event_time: datetime
    contact_type: ContactType
    contact_detail: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PostListItem(BaseModel):
    id: int
    post_type: PostType
    title: str
    category: Category
    image_path: Optional[str]
    location: CampusLocation
    event_time: datetime
    created_at: datetime

    model_config = {"from_attributes": True}
