from typing import Optional

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app import models
from app.auth.jwt_utils import JwtError, decode_token
from app.database import get_db


def _parse_token(header: Optional[str]) -> Optional[str]:
    if header and header.lower().startswith("bearer "):
        return header[7:].strip()
    return None


def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> models.User:
    token = _parse_token(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="未登录")
    try:
        payload = decode_token(token)
    except JwtError:
        raise HTTPException(status_code=401, detail="登录已失效，请重新登录")
    user = db.query(models.User).filter(models.User.id == int(payload["sub"])).first()
    if user is None:
        raise HTTPException(status_code=401, detail="登录已失效，请重新登录")
    return user


def get_current_user_optional(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> Optional[models.User]:
    token = _parse_token(authorization)
    if not token:
        return None
    try:
        payload = decode_token(token)
    except JwtError:
        return None
    return db.query(models.User).filter(models.User.id == int(payload["sub"])).first()
