import os
from datetime import datetime, timedelta, timezone

import jwt

_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")
_ALG = "HS256"
_EXPIRE_DAYS = 7


class JwtError(Exception):
    pass


def create_token(user_id: int, username: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "username": username,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(days=_EXPIRE_DAYS)).timestamp()),
    }
    return jwt.encode(payload, _SECRET, algorithm=_ALG)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, _SECRET, algorithms=[_ALG])
    except jwt.PyJWTError as e:
        raise JwtError(str(e)) from e
