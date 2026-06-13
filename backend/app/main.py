import os
from fastapi import FastAPI

app = FastAPI(title="南哪寻宝 API")


def init_app_state() -> None:
    from app.database import init_db
    init_db()
    upload_dir = os.getenv("NJU_UPLOAD_DIR", "./uploads")
    os.makedirs(upload_dir, exist_ok=True)


@app.on_event("startup")
def _startup():
    init_app_state()


@app.get("/api/health")
def health():
    return {"status": "ok"}
