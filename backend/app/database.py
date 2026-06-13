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
    _ensure_column("posts", "anon_id", "anon_id VARCHAR(36)")


def _ensure_column(table: str, column: str, ddl: str) -> None:
    from sqlalchemy import inspect, text
    insp = inspect(engine)
    if table not in insp.get_table_names():
        return
    cols = {c["name"] for c in insp.get_columns(table)}
    if column in cols:
        return
    with engine.begin() as conn:
        conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {ddl}"))


def get_db():
    assert SessionLocal is not None, "init_db() 必须先被调用"
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
