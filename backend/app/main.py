import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


def init_app_state() -> None:
    """初始化数据库与 uploads 目录；在 lifespan 与测试夹具中均会调用。"""
    from app.database import init_db
    init_db()
    upload_dir = os.getenv("NJU_UPLOAD_DIR", "./uploads")
    os.makedirs(upload_dir, exist_ok=True)
    # 重新挂载 /uploads 路由以指向当前 upload_dir（测试隔离场景）
    _mount_uploads(upload_dir)


def _mount_uploads(upload_dir: str) -> None:
    # 移除已存在的 /uploads mount，再重新挂载（兼容测试每个用例临时目录）
    app.router.routes = [
        r for r in app.router.routes
        if not (getattr(r, "path", None) == "/uploads")
    ]
    app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_app_state()
    yield


app = FastAPI(title="南哪寻宝 API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


from app.routers import posts as posts_router  # noqa: E402
from app.routers import comments as comments_router  # noqa: E402
app.include_router(posts_router.router)
app.include_router(comments_router.router)
