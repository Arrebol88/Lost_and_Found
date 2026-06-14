import os
import shutil

from sqlalchemy import create_engine, inspect, text
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
    _purge_legacy_anon_schema()
    Base.metadata.create_all(bind=engine)


def _purge_legacy_anon_schema() -> None:
    """检测旧版 anon_id schema，若存在则丢弃旧表与上传文件，让 create_all 重建。"""
    insp = inspect(engine)
    table_names = set(insp.get_table_names())
    if "posts" not in table_names:
        return
    posts_cols = {c["name"] for c in insp.get_columns("posts")}
    if "anon_id" not in posts_cols:
        return
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS post_comments"))
        conn.execute(text("DROP TABLE IF EXISTS post_likes"))
        conn.execute(text("DROP TABLE IF EXISTS posts"))
    upload_dir = os.getenv("NJU_UPLOAD_DIR", "./uploads")
    if os.path.isdir(upload_dir):
        for entry in os.listdir(upload_dir):
            target = os.path.join(upload_dir, entry)
            if os.path.isdir(target):
                shutil.rmtree(target, ignore_errors=True)
            else:
                try:
                    os.remove(target)
                except OSError:
                    pass


def get_db():
    assert SessionLocal is not None, "init_db() 必须先被调用"
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
