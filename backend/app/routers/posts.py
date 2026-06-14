from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import models, storage
from app.auth.deps import get_current_user, get_current_user_optional
from app.database import get_db
from app.schemas import (
    CampusLocation,
    Category,
    LikeToggleOut,
    PostCreate,
    PostDetailOut,
    PostListItem,
    PostOut,
    PostType,
    TimeRange,
)

router = APIRouter(prefix="/api", tags=["posts"])


def _post_to_out(post: models.Post) -> dict:
    return {
        "id": post.id,
        "post_type": post.post_type,
        "title": post.title,
        "category": post.category,
        "image_path": post.image_path,
        "description": post.description,
        "location": post.location,
        "event_time": post.event_time,
        "contact_type": post.contact_type,
        "contact_detail": post.contact_detail,
        "created_at": post.created_at,
        "author_username": post.author.username if post.author else "",
    }


@router.get("/posts", response_model=List[PostListItem])
def list_posts(
    post_type: Optional[PostType] = Query(None),
    category: Optional[Category] = Query(None),
    location: Optional[CampusLocation] = Query(None),
    time_range: Optional[TimeRange] = Query(None),
    mine: Optional[bool] = Query(False),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current: Optional[models.User] = Depends(get_current_user_optional),
):
    if mine and current is None:
        raise HTTPException(status_code=401, detail="未登录")

    query = db.query(models.Post)
    if mine and current is not None:
        query = query.filter(models.Post.user_id == current.id)
    elif post_type is not None:
        query = query.filter(models.Post.post_type == post_type.value)

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

    items = query.order_by(models.Post.created_at.desc()).offset(offset).limit(limit).all()
    return [
        PostListItem.model_validate(
            {
                **{k: getattr(p, k) for k in PostListItem.model_fields if k != "author_username"},
                "author_username": p.author.username if p.author else "",
            }
        )
        for p in items
    ]


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
    current: models.User = Depends(get_current_user),
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
        user_id=current.id,
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

    return _post_to_out(post)


def _first_error(e: ValidationError) -> str:
    err = e.errors()[0]
    loc = ".".join(str(x) for x in err.get("loc", []))
    return f"{loc}: {err.get('msg', '校验失败')}"


@router.get("/posts/{post_id}", response_model=PostDetailOut)
def get_post(
    post_id: int,
    db: Session = Depends(get_db),
    current: Optional[models.User] = Depends(get_current_user_optional),
):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="post not found")
    like_count = (
        db.query(models.PostLike)
        .filter(models.PostLike.post_id == post_id)
        .count()
    )
    liked = False
    mine = False
    if current is not None:
        liked = (
            db.query(models.PostLike)
            .filter(
                models.PostLike.post_id == post_id,
                models.PostLike.user_id == current.id,
            )
            .first()
            is not None
        )
        mine = post.user_id == current.id
    base = _post_to_out(post)
    return PostDetailOut(**base, like_count=like_count, liked_by_me=liked, mine=mine)


@router.post("/posts/{post_id}/likes", response_model=LikeToggleOut)
def toggle_like(
    post_id: int,
    db: Session = Depends(get_db),
    current: models.User = Depends(get_current_user),
):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="post not found")
    existing = (
        db.query(models.PostLike)
        .filter(
            models.PostLike.post_id == post_id,
            models.PostLike.user_id == current.id,
        )
        .first()
    )
    if existing is None:
        db.add(models.PostLike(post_id=post_id, user_id=current.id))
        db.commit()
        liked = True
    else:
        db.delete(existing)
        db.commit()
        liked = False
    count = (
        db.query(models.PostLike)
        .filter(models.PostLike.post_id == post_id)
        .count()
    )
    return LikeToggleOut(liked=liked, like_count=count)


@router.put("/posts/{post_id}", response_model=PostDetailOut)
def update_post(
    post_id: int,
    title: str = Form(...),
    category: str = Form(...),
    description: Optional[str] = Form(None),
    location: str = Form(...),
    event_time: str = Form(...),
    contact_type: str = Form(...),
    contact_detail: str = Form(...),
    image: Optional[UploadFile] = File(None),
    remove_image: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current: models.User = Depends(get_current_user),
):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="post not found")
    if post.user_id != current.id:
        raise HTTPException(status_code=403, detail="not your post")

    try:
        parsed_time = datetime.fromisoformat(event_time)
    except ValueError:
        raise HTTPException(status_code=400, detail="event_time 格式必须是 ISO 8601")

    try:
        payload = PostCreate(
            post_type=post.post_type,
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

    new_image_rel: Optional[str] = None
    if image is not None and image.filename:
        data = image.file.read()
        try:
            new_image_rel = storage.save_image(
                filename=image.filename,
                content=data,
                content_type=image.content_type or "",
            )
        except storage.ImageTooLargeError as e:
            raise HTTPException(status_code=413, detail=str(e))
        except storage.InvalidImageError as e:
            raise HTTPException(status_code=400, detail=str(e))

    old_image_rel = post.image_path
    drop_old = False
    if new_image_rel is not None:
        post.image_path = new_image_rel
        drop_old = bool(old_image_rel)
    elif (remove_image or "").lower() in ("true", "1", "yes"):
        post.image_path = None
        drop_old = bool(old_image_rel)

    post.title = payload.title
    post.category = payload.category.value
    post.description = payload.description
    post.location = payload.location.value
    post.event_time = payload.event_time
    post.contact_type = payload.contact_type.value
    post.contact_detail = payload.contact_detail

    try:
        db.commit()
        db.refresh(post)
    except Exception:
        db.rollback()
        if new_image_rel:
            storage.delete_image(new_image_rel)
        raise HTTPException(status_code=500, detail="数据库写入失败")

    if drop_old and old_image_rel:
        storage.delete_image(old_image_rel)

    like_count = (
        db.query(models.PostLike)
        .filter(models.PostLike.post_id == post_id)
        .count()
    )
    liked = (
        db.query(models.PostLike)
        .filter(
            models.PostLike.post_id == post_id,
            models.PostLike.user_id == current.id,
        )
        .first()
        is not None
    )
    base = _post_to_out(post)
    return PostDetailOut(**base, like_count=like_count, liked_by_me=liked, mine=True)


@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current: models.User = Depends(get_current_user),
):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="post not found")
    if post.user_id != current.id:
        raise HTTPException(status_code=403, detail="not your post")

    comments = (
        db.query(models.PostComment)
        .filter(models.PostComment.post_id == post_id)
        .all()
    )
    comment_images = [c.image_path for c in comments if c.image_path]
    main_image = post.image_path

    db.query(models.PostComment).filter(models.PostComment.post_id == post_id).delete(synchronize_session=False)
    db.query(models.PostLike).filter(models.PostLike.post_id == post_id).delete(synchronize_session=False)
    db.delete(post)
    db.commit()

    for rel in comment_images:
        storage.delete_image(rel)
    if main_image:
        storage.delete_image(main_image)
    return None
