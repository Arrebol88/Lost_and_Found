from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, storage
from app.routers.posts import get_anon_id
from app.schemas import CommentOut

router = APIRouter(prefix="/api", tags=["comments"])


def _to_out(c: models.PostComment, anon_id: str) -> CommentOut:
    return CommentOut(
        id=c.id,
        post_id=c.post_id,
        content=c.content,
        image_path=c.image_path,
        created_at=c.created_at,
        mine=(c.anon_id == anon_id),
    )


@router.get("/posts/{post_id}/comments", response_model=List[CommentOut])
def list_comments(
    post_id: int,
    db: Session = Depends(get_db),
    anon_id: str = Depends(get_anon_id),
):
    if db.query(models.Post).filter(models.Post.id == post_id).first() is None:
        raise HTTPException(status_code=404, detail="post not found")
    rows = (
        db.query(models.PostComment)
        .filter(models.PostComment.post_id == post_id)
        .order_by(
            models.PostComment.created_at.desc(),
            models.PostComment.id.desc(),
        )
        .all()
    )
    return [_to_out(r, anon_id) for r in rows]


@router.post(
    "/posts/{post_id}/comments",
    response_model=CommentOut,
    status_code=status.HTTP_201_CREATED,
)
def create_comment(
    post_id: int,
    content: str = Form(...),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    anon_id: str = Depends(get_anon_id),
):
    if db.query(models.Post).filter(models.Post.id == post_id).first() is None:
        raise HTTPException(status_code=404, detail="post not found")
    text = (content or "").strip()
    if not text or len(text) > 200:
        raise HTTPException(status_code=400, detail="content: 1..200 字符")

    image_rel: Optional[str] = None
    if image is not None and image.filename:
        data = image.file.read()
        try:
            image_rel = storage.save_image(
                filename=image.filename,
                content=data,
                content_type=image.content_type or "",
            )
        except storage.ImageTooLargeError as e:
            raise HTTPException(status_code=413, detail=str(e))
        except storage.InvalidImageError as e:
            raise HTTPException(status_code=400, detail=str(e))

    row = models.PostComment(
        post_id=post_id,
        anon_id=anon_id,
        content=text,
        image_path=image_rel,
    )
    try:
        db.add(row)
        db.commit()
        db.refresh(row)
    except Exception:
        db.rollback()
        if image_rel:
            storage.delete_image(image_rel)
        raise HTTPException(status_code=500, detail="数据库写入失败")
    return _to_out(row, anon_id)


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    anon_id: str = Depends(get_anon_id),
):
    row = (
        db.query(models.PostComment)
        .filter(models.PostComment.id == comment_id)
        .first()
    )
    if row is None:
        raise HTTPException(status_code=404, detail="comment not found")
    if row.anon_id != anon_id:
        raise HTTPException(status_code=403, detail="not your comment")
    rel = row.image_path
    db.delete(row)
    db.commit()
    if rel:
        storage.delete_image(rel)
    return None
