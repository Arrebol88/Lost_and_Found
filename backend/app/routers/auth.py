from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models
from app.auth.deps import get_current_user
from app.auth.jwt_utils import create_token
from app.auth.password import hash_password, verify_password
from app.database import get_db
from app.schemas import LoginIn, RegisterIn, TokenOut, UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.username.ilike(payload.username)).first()
    if existing is not None:
        raise HTTPException(status_code=409, detail="用户名已被占用")
    user = models.User(username=payload.username, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return TokenOut(token=create_token(user.id, user.username), user=UserOut.model_validate(user))


@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username.ilike(payload.username)).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    return TokenOut(token=create_token(user.id, user.username), user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
def me(current: models.User = Depends(get_current_user)):
    return UserOut.model_validate(current)
