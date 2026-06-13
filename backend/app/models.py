from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, CheckConstraint
from app.database import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    post_type = Column(String(16), nullable=False)
    title = Column(String(50), nullable=False)
    category = Column(String(32), nullable=False)
    image_path = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    location = Column(String(100), nullable=False)
    event_time = Column(DateTime, nullable=False)
    contact_type = Column(String(32), nullable=False)
    contact_detail = Column(String(200), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    __table_args__ = (
        CheckConstraint("post_type IN ('found','lost')", name="ck_post_type"),
        CheckConstraint(
            "category IN ('electronics','id_card','bag','accessory','clothing',"
            "'daily','study','sports','personal_care')",
            name="ck_category",
        ),
        CheckConstraint(
            "location IN ('gulou','xianlin','suzhou','pukou')",
            name="ck_location",
        ),
        CheckConstraint(
            "contact_type IN ('self_pickup','contact','handed_over','owner_contact')",
            name="ck_contact_type",
        ),
        CheckConstraint(
            "(post_type='lost' AND contact_type='owner_contact') OR "
            "(post_type='found' AND contact_type IN ('self_pickup','contact','handed_over'))",
            name="ck_post_contact_match",
        ),
    )
