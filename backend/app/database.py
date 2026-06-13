import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()

# 模块级状态：engine 与 SessionLocal 在 init_db() 时根据当前环境变量初始化
engine = None
SessionLocal = None


def init_db() -> None:
    global engine, SessionLocal
    db_url = os.getenv("NJU_DB_URL", "sqlite:///./nju_lostfound.db")
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    from app import models  # noqa: F401  注册模型到 metadata
    Base.metadata.create_all(bind=engine)


def get_db():
    assert SessionLocal is not None, "init_db() 必须先被调用"
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
