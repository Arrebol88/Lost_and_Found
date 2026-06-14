from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, CheckConstraint,
    ForeignKey, UniqueConstraint, Index,
)
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(32), nullable=False, unique=True)
    password_hash = Column(String(128), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)


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
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    author = relationship("User", lazy="joined")

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


class PostLike(Base):
    __tablename__ = "post_likes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    __table_args__ = (
        UniqueConstraint("post_id", "user_id", name="uq_post_likes_post_user"),
    )


class PostComment(Base):
    __tablename__ = "post_comments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(String(200), nullable=False)
    image_path = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    author = relationship("User", lazy="joined")

    __table_args__ = (
        Index("ix_post_comments_post_created", "post_id", "created_at"),
    )
