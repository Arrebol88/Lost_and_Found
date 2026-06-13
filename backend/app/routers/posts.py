from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session
from pydantic import ValidationError

from app.database import get_db
from app import models, storage
from app.schemas import (
    CampusLocation,
    Category,
    PostCreate,
    PostListItem,
    PostOut,
    PostType,
    TimeRange,
)

router = APIRouter(prefix="/api", tags=["posts"])


@router.get("/posts", response_model=List[PostListItem])
def list_posts(
    post_type: PostType = Query(...),
    category: Optional[Category] = Query(None),
    location: Optional[CampusLocation] = Query(None),
    time_range: Optional[TimeRange] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(models.Post).filter(models.Post.post_type == post_type.value)

    if category is not None:
        query = query.filter(models.Post.category == category.value)
    if location is not None:
        query = query.filter(models.Post.location == location.value)
    if time_range is not None:
        now = datetime.now()
        if time_range == TimeRange.within_1d:
            query = query.filter(models.Post.event_time >= now - timedelta(days=1))
        elif time_range == TimeRange.within_3d:
            query = query.filter(models.Post.event_time >= now - timedelta(days=3))
        elif time_range == TimeRange.within_7d:
            query = query.filter(models.Post.event_time >= now - timedelta(days=7))
        elif time_range == TimeRange.older_than_7d:
            query = query.filter(models.Post.event_time < now - timedelta(days=7))

    return query.order_by(models.Post.created_at.desc()).offset(offset).limit(limit).all()


@router.post("/posts", response_model=PostOut, status_code=status.HTTP_201_CREATED)
def create_post(
    post_type: str = Form(...),
    title: str = Form(...),
    category: str = Form(...),
    description: Optional[str] = Form(None),
    location: str = Form(...),
    event_time: str = Form(...),
    contact_type: str = Form(...),
    contact_detail: str = Form(...),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    try:
        parsed_time = datetime.fromisoformat(event_time)
    except ValueError:
        raise HTTPException(status_code=400, detail="event_time 格式必须是 ISO 8601")

    try:
        payload = PostCreate(
            post_type=post_type,
            title=title,
            category=category,
            description=description,
            location=location,
            event_time=parsed_time,
            contact_type=contact_type,
            contact_detail=contact_detail,
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=_first_error(e))

    image_rel: Optional[str] = None
    if image is not None and image.filename:
        content = image.file.read()
        try:
            image_rel = storage.save_image(
                filename=image.filename,
                content=content,
                content_type=image.content_type or "",
            )
        except storage.ImageTooLargeError as e:
            raise HTTPException(status_code=413, detail=str(e))
        except storage.InvalidImageError as e:
            raise HTTPException(status_code=400, detail=str(e))

    post = models.Post(
        post_type=payload.post_type.value,
        title=payload.title,
        category=payload.category.value,
        image_path=image_rel,
        description=payload.description,
        location=payload.location.value,
        event_time=payload.event_time,
        contact_type=payload.contact_type.value,
        contact_detail=payload.contact_detail,
    )
    try:
        db.add(post)
        db.commit()
        db.refresh(post)
    except Exception:
        db.rollback()
        if image_rel:
            storage.delete_image(image_rel)
        raise HTTPException(status_code=500, detail="数据库写入失败")

    return post


def _first_error(e: ValidationError) -> str:
    err = e.errors()[0]
    loc = ".".join(str(x) for x in err.get("loc", []))
    return f"{loc}: {err.get('msg', '校验失败')}"
