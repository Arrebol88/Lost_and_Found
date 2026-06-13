# 南哪寻宝 · 发帖功能实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 实现"南哪寻宝"网站的发帖闭环：首页发帖按钮 → 类型选择（寻物 / 寻主）→ 表单提交 → FastAPI 入库（含图片到 `uploads/`），全程 TDD。

**架构：** 前后端分离。后端 FastAPI + SQLite + SQLAlchemy + Pydantic，单表 `posts`；图片存本地文件系统、DB 存路径。前端 Vue 3 + Vite，三个视图（首页 / 类型选择 / 表单）由条件渲染切换。Docker 双镜像 + docker-compose 一键启动。

**技术栈：** Python 3.11、FastAPI 0.115、SQLAlchemy 2.x、Pydantic v2、Uvicorn、pytest + httpx、Vue 3、Vite 5、axios、Vitest + @vue/test-utils。

**对应规格：** [SPEC](file:///c:/Desktop/program/docs/superpowers/specs/2026-06-13-post-creation-design.md)

---

## 文件结构

```
program/
├── backend/
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── pytest.ini
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── storage.py
│   │   └── routers/
│   │       ├── __init__.py
│   │       └── posts.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_health.py
│   │   ├── test_posts_success.py
│   │   ├── test_posts_validation.py
│   │   └── test_posts_image.py
│   └── uploads/.gitkeep
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   ├── Dockerfile
│   ├── src/
│   │   ├── main.js
│   │   ├── App.vue
│   │   ├── api.js
│   │   └── components/
│   │       ├── TypePicker.vue
│   │       └── PostForm.vue
│   └── tests/
│       ├── TypePicker.test.js
│       └── PostForm.test.js
├── docker-compose.yml
├── Makefile
├── .github/workflows/ci.yml
├── .gitignore
├── README.md
└── AGENT_LOG.md
```

---

## 任务 1：仓库脚手架与 .gitignore

**文件：**
- 创建：`.gitignore`
- 创建：`README.md`
- 创建：`AGENT_LOG.md`
- 创建：`backend/uploads/.gitkeep`

- [ ] **步骤 1：写 `.gitignore`**

```gitignore
__pycache__/
*.pyc
.venv/
.pytest_cache/
*.egg-info/
node_modules/
dist/
.vite/
.idea/
.vscode/
.DS_Store
Thumbs.db
backend/uploads/**
!backend/uploads/.gitkeep
backend/*.db
backend/*.db-journal
backend/*.db-wal
backend/*.db-shm
```

- [ ] **步骤 2：写最小 `README.md`**

```markdown
# 南哪寻宝（NJU LostFound）

南京大学失物招领与寻物启事平台。本仓库当前实现"发帖闭环"。

## 快速开始

\`\`\`bash
docker compose up --build
# 前端：http://localhost:5173
# 后端：http://localhost:8000/api/health
\`\`\`

详见 SPEC 与 PLAN：docs/superpowers/。
```

- [ ] **步骤 3：写 `AGENT_LOG.md` 骨架**

```markdown
# AGENT_LOG

按时间倒序记录关键节点。

## 2026-06-13
- 完成 SPEC 与 PLAN（brainstorming + writing-plans 技能）
```

- [ ] **步骤 4：创建 `backend/uploads/.gitkeep`**（空文件）

- [ ] **步骤 5：Commit**

```bash
git add .gitignore README.md AGENT_LOG.md backend/uploads/.gitkeep
git commit -m "chore: 初始化仓库脚手架与 .gitignore"
```

---

## 任务 2：后端依赖与 pytest 配置

**文件：**
- 创建：`backend/requirements.txt`
- 创建：`backend/pytest.ini`
- 创建：`backend/app/__init__.py`、`backend/app/routers/__init__.py`、`backend/tests/__init__.py`（空文件）

- [ ] **步骤 1：`backend/requirements.txt`**

```
fastapi==0.115.0
uvicorn[standard]==0.30.6
sqlalchemy==2.0.34
pydantic==2.9.2
python-multipart==0.0.9
httpx==0.27.2
pytest==8.3.3
pytest-asyncio==0.24.0
```

- [ ] **步骤 2：`backend/pytest.ini`**

```ini
[pytest]
testpaths = tests
python_files = test_*.py
asyncio_mode = auto
```

- [ ] **步骤 3：创建三个空 `__init__.py`**（`app/`、`app/routers/`、`tests/`）

- [ ] **步骤 4：本地装依赖验证**

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

预期：全部安装成功，无依赖冲突。

- [ ] **步骤 5：Commit**

```bash
git add backend/requirements.txt backend/pytest.ini backend/app/__init__.py backend/app/routers/__init__.py backend/tests/__init__.py
git commit -m "feat(backend): 添加依赖清单与 pytest 配置"
```

---

## 任务 3：后端 health 接口（TDD 红绿）

**文件：**
- 创建：`backend/tests/conftest.py`
- 创建：`backend/tests/test_health.py`
- 创建：`backend/app/database.py`
- 创建：`backend/app/main.py`

- [ ] **步骤 1：写 `backend/tests/conftest.py`**

```python
import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path, monkeypatch):
    db_file = tmp_path / "test.db"
    uploads_dir = tmp_path / "uploads"
    uploads_dir.mkdir()
    monkeypatch.setenv("NJU_DB_URL", f"sqlite:///{db_file}")
    monkeypatch.setenv("NJU_UPLOAD_DIR", str(uploads_dir))

    # 重新加载模块以读取环境变量
    import importlib
    from app import database
    importlib.reload(database)
    from app import main
    importlib.reload(main)

    main.init_app_state()
    return TestClient(main.app)
```

- [ ] **步骤 2：写失败测试 `backend/tests/test_health.py`**

```python
def test_health_ok(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
```

- [ ] **步骤 3：运行验证失败**

```bash
cd backend && pytest tests/test_health.py -v
```

预期：FAIL，`ModuleNotFoundError`。

- [ ] **步骤 4：写最小 `backend/app/database.py`**

```python
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DB_URL = os.getenv("NJU_DB_URL", "sqlite:///./nju_lostfound.db")
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **步骤 5：写最小 `backend/app/main.py`**

```python
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
```

- [ ] **步骤 6：运行验证通过**

```bash
cd backend && pytest tests/test_health.py -v
```

预期：1 passed。

- [ ] **步骤 7：Commit**

```bash
git add backend/app/main.py backend/app/database.py backend/tests/conftest.py backend/tests/test_health.py
git commit -m "feat(backend): 健康检查接口与测试夹具"
```

---

## 任务 4：Post 模型与表结构

**文件：**
- 创建：`backend/app/models.py`
- 修改：`backend/app/database.py`

- [ ] **步骤 1：在 `backend/tests/test_health.py` 末尾追加失败测试**

```python
def test_posts_table_exists(client):
    from sqlalchemy import inspect
    from app.database import engine
    insp = inspect(engine)
    assert "posts" in insp.get_table_names()
    cols = {c["name"] for c in insp.get_columns("posts")}
    expected = {
        "id", "post_type", "title", "category", "image_path",
        "description", "location", "event_time",
        "contact_type", "contact_detail", "created_at",
    }
    assert expected.issubset(cols)
```

- [ ] **步骤 2：运行验证失败**

```bash
cd backend && pytest tests/test_health.py::test_posts_table_exists -v
```

预期：FAIL，`posts` 表不存在。

- [ ] **步骤 3：写 `backend/app/models.py`**

```python
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, CheckConstraint
from app.database import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    post_type = Column(String(16), nullable=False)
    title = Column(String(50), nullable=False)
    category = Column(String(32), nullable=False)
    image_path = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    location = Column(String(100), nullable=False)
    event_time = Column(DateTime, nullable=False)
    contact_type = Column(String(32), nullable=False)
    contact_detail = Column(String(200), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    __table_args__ = (
        CheckConstraint("post_type IN ('found','lost')", name="ck_post_type"),
        CheckConstraint(
            "category IN ('electronics','id_card','bag','accessory','clothing',"
            "'daily','study','sports','personal_care')",
            name="ck_category",
        ),
        CheckConstraint(
            "contact_type IN ('self_pickup','contact','handed_over','owner_contact')",
            name="ck_contact_type",
        ),
        CheckConstraint(
            "(post_type='lost' AND contact_type='owner_contact') OR "
            "(post_type='found' AND contact_type IN ('self_pickup','contact','handed_over'))",
            name="ck_post_contact_match",
        ),
    )
```

- [ ] **步骤 4：修改 `backend/app/database.py` 的 `init_db`**

将 `init_db` 替换为：

```python
def init_db() -> None:
    from app import models  # noqa: F401  注册模型到 metadata
    Base.metadata.create_all(bind=engine)
```

- [ ] **步骤 5：运行验证通过**

```bash
cd backend && pytest tests/test_health.py -v
```

预期：2 passed。

- [ ] **步骤 6：Commit**

```bash
git add backend/app/models.py backend/app/database.py backend/tests/test_health.py
git commit -m "feat(backend): Post 模型与 CHECK 约束"
```

---

## 任务 5：Pydantic schemas 与跨字段校验

**文件：**
- 创建：`backend/app/schemas.py`
- 创建：`backend/tests/test_posts_validation.py`

- [ ] **步骤 1：写失败测试 `backend/tests/test_posts_validation.py`**

```python
from datetime import datetime, timedelta
import pytest
from pydantic import ValidationError


def _payload(**overrides):
    base = dict(
        post_type="found",
        title="黑色雨伞",
        category="daily",
        description=None,
        location="逸夫楼 B201",
        event_time=datetime.now() - timedelta(hours=1),
        contact_type="self_pickup",
        contact_detail="工作日 8-17 自取",
    )
    base.update(overrides)
    return base


def test_valid_found_post():
    from app.schemas import PostCreate
    PostCreate(**_payload())


def test_valid_lost_post():
    from app.schemas import PostCreate
    PostCreate(**_payload(post_type="lost", contact_type="owner_contact",
                          contact_detail="微信 abc123"))


def test_lost_must_use_owner_contact():
    from app.schemas import PostCreate
    with pytest.raises(ValidationError):
        PostCreate(**_payload(post_type="lost", contact_type="self_pickup"))


def test_found_cannot_use_owner_contact():
    from app.schemas import PostCreate
    with pytest.raises(ValidationError):
        PostCreate(**_payload(contact_type="owner_contact"))


def test_event_time_in_future_rejected():
    from app.schemas import PostCreate
    with pytest.raises(ValidationError):
        PostCreate(**_payload(event_time=datetime.now() + timedelta(hours=1)))


def test_event_time_too_old_rejected():
    from app.schemas import PostCreate
    with pytest.raises(ValidationError):
        PostCreate(**_payload(event_time=datetime.now() - timedelta(days=400)))


def test_title_too_long_rejected():
    from app.schemas import PostCreate
    with pytest.raises(ValidationError):
        PostCreate(**_payload(title="x" * 51))


def test_invalid_category_rejected():
    from app.schemas import PostCreate
    with pytest.raises(ValidationError):
        PostCreate(**_payload(category="not_a_category"))
```

- [ ] **步骤 2：运行验证失败**

```bash
cd backend && pytest tests/test_posts_validation.py -v
```

预期：FAIL，`ModuleNotFoundError: app.schemas`。

- [ ] **步骤 3：写 `backend/app/schemas.py`**

```python
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator


class PostType(str, Enum):
    found = "found"
    lost = "lost"


class Category(str, Enum):
    electronics = "electronics"
    id_card = "id_card"
    bag = "bag"
    accessory = "accessory"
    clothing = "clothing"
    daily = "daily"
    study = "study"
    sports = "sports"
    personal_care = "personal_care"


class ContactType(str, Enum):
    self_pickup = "self_pickup"
    contact = "contact"
    handed_over = "handed_over"
    owner_contact = "owner_contact"


class PostCreate(BaseModel):
    post_type: PostType
    title: str = Field(..., min_length=1, max_length=50)
    category: Category
    description: Optional[str] = Field(None, max_length=500)
    location: str = Field(..., min_length=1, max_length=100)
    event_time: datetime
    contact_type: ContactType
    contact_detail: str = Field(..., min_length=1, max_length=200)

    @field_validator("event_time")
    @classmethod
    def _time_in_range(cls, v: datetime) -> datetime:
        now = datetime.now()
        if v > now:
            raise ValueError("丢失/捡到时间不能晚于当前时间")
        if v < now - timedelta(days=365):
            raise ValueError("丢失/捡到时间不能早于一年前")
        return v

    @model_validator(mode="after")
    def _contact_match_post_type(self):
        if self.post_type == PostType.lost and self.contact_type != ContactType.owner_contact:
            raise ValueError("寻物帖的联系方式类型必须是 owner_contact")
        if self.post_type == PostType.found and self.contact_type == ContactType.owner_contact:
            raise ValueError("寻主帖的联系方式类型必须是 自取/联系方式/已移交管理处")
        return self


class PostOut(BaseModel):
    id: int
    post_type: PostType
    title: str
    category: Category
    image_path: Optional[str]
    description: Optional[str]
    location: str
    event_time: datetime
    contact_type: ContactType
    contact_detail: str
    created_at: datetime

    model_config = {"from_attributes": True}
```

- [ ] **步骤 4：运行验证通过**

```bash
cd backend && pytest tests/test_posts_validation.py -v
```

预期：8 passed。

- [ ] **步骤 5：Commit**

```bash
git add backend/app/schemas.py backend/tests/test_posts_validation.py
git commit -m "feat(backend): Pydantic schemas 与跨字段校验"
```

---

## 任务 6：图片存储模块

**文件：**
- 创建：`backend/app/storage.py`
- 创建：`backend/tests/test_posts_image.py`

- [ ] **步骤 1：写失败测试 `backend/tests/test_posts_image.py`**

```python
import pytest

PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\xcf"
    b"\xc0\x00\x00\x00\x03\x00\x01\x5b\x6e\x40\x9b\x00\x00\x00\x00IEND\xaeB`\x82"
)


def test_save_valid_png(tmp_path, monkeypatch):
    monkeypatch.setenv("NJU_UPLOAD_DIR", str(tmp_path))
    from app.storage import save_image
    rel = save_image(filename="a.png", content=PNG_BYTES, content_type="image/png")
    assert rel.startswith("uploads/")
    assert rel.endswith(".png")
    abs_path = tmp_path / rel.split("uploads/", 1)[1]
    assert abs_path.exists()
    assert abs_path.read_bytes() == PNG_BYTES


def test_reject_oversize(tmp_path, monkeypatch):
    monkeypatch.setenv("NJU_UPLOAD_DIR", str(tmp_path))
    from app.storage import save_image, ImageTooLargeError
    big = b"\x89PNG\r\n\x1a\n" + b"\x00" * (5 * 1024 * 1024 + 1)
    with pytest.raises(ImageTooLargeError):
        save_image(filename="big.png", content=big, content_type="image/png")


def test_reject_fake_extension(tmp_path, monkeypatch):
    monkeypatch.setenv("NJU_UPLOAD_DIR", str(tmp_path))
    from app.storage import save_image, InvalidImageError
    fake = b"MZ\x90\x00" + b"\x00" * 100
    with pytest.raises(InvalidImageError):
        save_image(filename="evil.jpg", content=fake, content_type="image/jpeg")


def test_reject_unsupported_mime(tmp_path, monkeypatch):
    monkeypatch.setenv("NJU_UPLOAD_DIR", str(tmp_path))
    from app.storage import save_image, InvalidImageError
    with pytest.raises(InvalidImageError):
        save_image(filename="a.gif", content=b"GIF89a", content_type="image/gif")
```

- [ ] **步骤 2：运行验证失败**

```bash
cd backend && pytest tests/test_posts_image.py -v
```

预期：FAIL，`ModuleNotFoundError: app.storage`。

- [ ] **步骤 3：写 `backend/app/storage.py`**

```python
import os
import uuid
from datetime import datetime
from pathlib import Path

MAX_BYTES = 5 * 1024 * 1024
ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp"}
EXT_BY_MIME = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}

SIGNATURES = {
    "image/jpeg": [b"\xff\xd8\xff"],
    "image/png": [b"\x89PNG\r\n\x1a\n"],
    "image/webp": [b"RIFF"],
}


class InvalidImageError(ValueError):
    pass


class ImageTooLargeError(ValueError):
    pass


def _upload_root() -> Path:
    return Path(os.getenv("NJU_UPLOAD_DIR", "./uploads"))


def _check_signature(content: bytes, content_type: str) -> bool:
    if content_type not in SIGNATURES:
        return False
    if not any(content.startswith(sig) for sig in SIGNATURES[content_type]):
        return False
    if content_type == "image/webp":
        if len(content) < 12 or content[8:12] != b"WEBP":
            return False
    return True


def save_image(*, filename: str, content: bytes, content_type: str) -> str:
    if content_type not in ALLOWED_MIME:
        raise InvalidImageError(f"不支持的图片类型：{content_type}")
    if len(content) > MAX_BYTES:
        raise ImageTooLargeError("图片超过 5MB 限制")
    if not _check_signature(content, content_type):
        raise InvalidImageError("图片内容与扩展名不匹配")

    now = datetime.now()
    sub = Path(f"{now.year:04d}/{now.month:02d}/{now.day:02d}")
    target_dir = _upload_root() / sub
    target_dir.mkdir(parents=True, exist_ok=True)
    name = f"{uuid.uuid4().hex}{EXT_BY_MIME[content_type]}"
    abs_path = target_dir / name
    abs_path.write_bytes(content)
    return f"uploads/{sub.as_posix()}/{name}"


def delete_image(rel_path: str) -> None:
    if not rel_path or not rel_path.startswith("uploads/"):
        return
    abs_path = _upload_root() / rel_path.split("uploads/", 1)[1]
    try:
        abs_path.unlink(missing_ok=True)
    except OSError:
        pass
```

- [ ] **步骤 4：运行验证通过**

```bash
cd backend && pytest tests/test_posts_image.py -v
```

预期：4 passed。

- [ ] **步骤 5：Commit**

```bash
git add backend/app/storage.py backend/tests/test_posts_image.py
git commit -m "feat(backend): 图片存储模块（MIME + magic bytes 双校验）"
```

---

## 任务 7：POST /api/posts 主路径

**文件：**
- 创建：`backend/app/routers/posts.py`
- 修改：`backend/app/main.py`
- 创建：`backend/tests/test_posts_success.py`

- [ ] **步骤 1：写失败测试 `backend/tests/test_posts_success.py`**

```python
from datetime import datetime, timedelta
import os


def _form(**overrides):
    base = {
        "post_type": "found",
        "title": "黑色雨伞",
        "category": "daily",
        "description": "长柄",
        "location": "逸夫楼 B201",
        "event_time": (datetime.now() - timedelta(hours=1)).isoformat(timespec="minutes"),
        "contact_type": "self_pickup",
        "contact_detail": "工作日 8-17 自取",
    }
    base.update(overrides)
    return base


def test_create_lost_post_no_image(client):
    r = client.post("/api/posts", data=_form(
        post_type="lost", contact_type="owner_contact", contact_detail="微信 abc123"))
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["id"] >= 1
    assert body["post_type"] == "lost"
    assert body["image_path"] is None


def test_create_found_post_with_png(client):
    PNG = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\xcf"
        b"\xc0\x00\x00\x00\x03\x00\x01\x5b\x6e\x40\x9b\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    r = client.post(
        "/api/posts",
        data=_form(),
        files={"image": ("a.png", PNG, "image/png")},
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["image_path"].startswith("uploads/")
    assert body["image_path"].endswith(".png")
    upload_dir = os.environ["NJU_UPLOAD_DIR"]
    abs_p = os.path.join(upload_dir, body["image_path"].split("uploads/", 1)[1])
    assert os.path.exists(abs_p)
```

- [ ] **步骤 2：运行验证失败**

```bash
cd backend && pytest tests/test_posts_success.py -v
```

预期：FAIL，404。

- [ ] **步骤 3：写 `backend/app/routers/posts.py`**

```python
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from pydantic import ValidationError

from app.database import get_db
from app import models, storage
from app.schemas import PostCreate, PostOut

router = APIRouter(prefix="/api", tags=["posts"])


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
        location=payload.location,
        event_time=payload.event_time,
        contact_type=payload.contact_type.value,
        contact_detail=payload.contact_detail,
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

    return post


def _first_error(e: ValidationError) -> str:
    err = e.errors()[0]
    loc = ".".join(str(x) for x in err.get("loc", []))
    return f"{loc}: {err.get('msg', '校验失败')}"
```

- [ ] **步骤 4：修改 `backend/app/main.py`**

完整替换为：

```python
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="南哪寻宝 API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def init_app_state() -> None:
    from app.database import init_db
    init_db()
    upload_dir = os.getenv("NJU_UPLOAD_DIR", "./uploads")
    os.makedirs(upload_dir, exist_ok=True)
    if not any(r.path == "/uploads" for r in app.routes):
        app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")


@app.on_event("startup")
def _startup():
    init_app_state()


@app.get("/api/health")
def health():
    return {"status": "ok"}


from app.routers import posts as posts_router  # noqa: E402
app.include_router(posts_router.router)
```

- [ ] **步骤 5：运行验证通过**

```bash
cd backend && pytest tests/test_posts_success.py -v
```

预期：2 passed。

- [ ] **步骤 6：Commit**

```bash
git add backend/app/routers/posts.py backend/app/main.py backend/tests/test_posts_success.py
git commit -m "feat(backend): POST /api/posts 主路径（含图片落盘）"
```

---

## 任务 8：POST 错误分支与边界用例

**文件：**
- 修改：`backend/tests/test_posts_image.py`（追加 API 级用例）

- [ ] **步骤 1：在 `backend/tests/test_posts_image.py` 末尾追加**

```python
from datetime import datetime, timedelta


def _api_form(**overrides):
    base = {
        "post_type": "found",
        "title": "黑色雨伞",
        "category": "daily",
        "description": "长柄",
        "location": "逸夫楼 B201",
        "event_time": (datetime.now() - timedelta(hours=1)).isoformat(timespec="minutes"),
        "contact_type": "self_pickup",
        "contact_detail": "工作日 8-17 自取",
    }
    base.update(overrides)
    return base


def test_api_reject_lost_with_self_pickup(client):
    r = client.post("/api/posts", data=_api_form(post_type="lost"))
    assert r.status_code == 400


def test_api_reject_invalid_category(client):
    r = client.post("/api/posts", data=_api_form(category="not_a_category"))
    assert r.status_code == 400


def test_api_reject_event_time_in_future(client):
    future = (datetime.now() + timedelta(hours=1)).isoformat(timespec="minutes")
    r = client.post("/api/posts", data=_api_form(event_time=future))
    assert r.status_code == 400


def test_api_reject_oversize_image(client):
    big = b"\x89PNG\r\n\x1a\n" + b"\x00" * (5 * 1024 * 1024 + 1)
    r = client.post("/api/posts", data=_api_form(),
                    files={"image": ("big.png", big, "image/png")})
    assert r.status_code == 413


def test_api_reject_fake_image(client):
    fake = b"MZ\x90\x00" + b"\x00" * 100
    r = client.post("/api/posts", data=_api_form(),
                    files={"image": ("a.jpg", fake, "image/jpeg")})
    assert r.status_code == 400


def test_api_reject_title_51_chars(client):
    r = client.post("/api/posts", data=_api_form(title="x" * 51))
    assert r.status_code == 400
```

- [ ] **步骤 2：运行验证全部通过**

```bash
cd backend && pytest -v
```

预期：所有用例 passed。

- [ ] **步骤 3：Commit**

```bash
git add backend/tests/test_posts_image.py
git commit -m "test(backend): 覆盖发帖接口错误分支与边界用例"
```

---

## 任务 9：前端脚手架

**文件：**
- 创建：`frontend/package.json`、`frontend/vite.config.js`、`frontend/index.html`、`frontend/src/main.js`、`frontend/src/App.vue`

- [ ] **步骤 1：写 `frontend/package.json`**

```json
{
  "name": "nju-lostfound-frontend",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview --host 0.0.0.0",
    "test": "vitest run"
  },
  "dependencies": {
    "axios": "^1.7.7",
    "vue": "^3.5.10"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.1.4",
    "@vue/test-utils": "^2.4.6",
    "jsdom": "^25.0.1",
    "vite": "^5.4.8",
    "vitest": "^2.1.2"
  }
}
```

- [ ] **步骤 2：写 `frontend/vite.config.js`**

```javascript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8000',
      '/uploads': 'http://localhost:8000'
    }
  },
  test: {
    environment: 'jsdom',
    globals: true,
    include: ['tests/**/*.test.js']
  }
})
```

- [ ] **步骤 3：写 `frontend/index.html`**

```html
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>南哪寻宝</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.js"></script>
  </body>
</html>
```

- [ ] **步骤 4：写 `frontend/src/main.js`**

```javascript
import { createApp } from 'vue'
import App from './App.vue'

createApp(App).mount('#app')
```

- [ ] **步骤 5：写 `frontend/src/App.vue`（占位）**

```vue
<script setup>
import { ref } from 'vue'

const view = ref('home')
const postType = ref(null)

function openPicker() { view.value = 'picker' }
function pickType(t) { postType.value = t; view.value = 'form' }
function backHome() { view.value = 'home'; postType.value = null }
function onSubmitted() {
  alert('发布成功')
  backHome()
}
</script>

<template>
  <main class="page">
    <header class="title">南哪寻宝</header>

    <section v-if="view === 'home'" class="home">
      <button class="primary" data-testid="btn-create" @click="openPicker">发帖</button>
    </section>

    <section v-else-if="view === 'picker'" class="picker">
      <h2>选择帖子类型</h2>
      <button class="primary" @click="pickType('found')">我捡到了东西（寻主帖）</button>
      <button class="primary" @click="pickType('lost')">我丢了东西（寻物帖）</button>
      <button class="link" @click="backHome">返回</button>
    </section>

    <section v-else class="form-wrap">
      <p>表单将在任务 11 实装。当前 post_type = {{ postType }}</p>
      <button class="link" @click="backHome">返回</button>
    </section>
  </main>
</template>

<style>
:root { font-family: system-ui, -apple-system, "PingFang SC", sans-serif; }
.page { max-width: 640px; margin: 0 auto; padding: 32px 16px; }
.title { font-size: 24px; font-weight: 700; color: #0f172a; }
.home { display: flex; justify-content: center; padding: 96px 0; }
.picker { display: flex; flex-direction: column; gap: 16px; padding: 32px 0; }
.primary { background: #2563eb; color: white; border: 0; padding: 12px 20px;
  border-radius: 8px; font-size: 16px; cursor: pointer; }
.primary:hover { background: #1d4ed8; }
.link { background: transparent; border: 0; color: #2563eb; cursor: pointer; padding: 8px 0; }
</style>
```

- [ ] **步骤 6：装依赖并验证 build**

```bash
cd frontend
npm install
npm run build
```

预期：`dist/` 生成成功。

- [ ] **步骤 7：Commit**

```bash
git add frontend/package.json frontend/vite.config.js frontend/index.html frontend/src/main.js frontend/src/App.vue
git commit -m "feat(frontend): Vite + Vue 3 脚手架与首页占位"
```

---

## 任务 10：API 客户端 + TypePicker 组件

**文件：**
- 创建：`frontend/src/api.js`
- 创建：`frontend/src/components/TypePicker.vue`
- 创建：`frontend/tests/TypePicker.test.js`
- 修改：`frontend/src/App.vue`

- [ ] **步骤 1：写 `frontend/src/api.js`**

```javascript
import axios from 'axios'

const http = axios.create({ baseURL: '' })

export async function createPost(form) {
  const fd = new FormData()
  Object.entries(form).forEach(([k, v]) => {
    if (v === null || v === undefined || v === '') return
    fd.append(k, v)
  })
  const r = await http.post('/api/posts', fd, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return r.data
}
```

- [ ] **步骤 2：写失败测试 `frontend/tests/TypePicker.test.js`**

```javascript
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import TypePicker from '../src/components/TypePicker.vue'

describe('TypePicker', () => {
  it('点击寻主帖按钮 emit found', async () => {
    const w = mount(TypePicker)
    await w.get('[data-testid="btn-found"]').trigger('click')
    expect(w.emitted().pick[0]).toEqual(['found'])
  })

  it('点击寻物帖按钮 emit lost', async () => {
    const w = mount(TypePicker)
    await w.get('[data-testid="btn-lost"]').trigger('click')
    expect(w.emitted().pick[0]).toEqual(['lost'])
  })

  it('点击返回 emit cancel', async () => {
    const w = mount(TypePicker)
    await w.get('[data-testid="btn-cancel"]').trigger('click')
    expect(w.emitted().cancel).toBeTruthy()
  })
})
```

- [ ] **步骤 3：运行验证失败**

```bash
cd frontend && npm test
```

预期：FAIL，找不到 `TypePicker.vue`。

- [ ] **步骤 4：写 `frontend/src/components/TypePicker.vue`**

```vue
<script setup>
const emit = defineEmits(['pick', 'cancel'])
</script>

<template>
  <div class="picker">
    <h2>选择帖子类型</h2>
    <button class="primary" data-testid="btn-found" @click="emit('pick', 'found')">
      我捡到了东西（寻主帖）
    </button>
    <button class="primary" data-testid="btn-lost" @click="emit('pick', 'lost')">
      我丢了东西（寻物帖）
    </button>
    <button class="link" data-testid="btn-cancel" @click="emit('cancel')">返回</button>
  </div>
</template>

<style scoped>
.picker { display: flex; flex-direction: column; gap: 16px; padding: 32px 0; }
.primary { background: #2563eb; color: white; border: 0; padding: 12px 20px;
  border-radius: 8px; font-size: 16px; cursor: pointer; }
.primary:hover { background: #1d4ed8; }
.link { background: transparent; border: 0; color: #2563eb; cursor: pointer; padding: 8px 0; }
</style>
```

- [ ] **步骤 5：修改 `frontend/src/App.vue`**

在 `<script setup>` 顶部增加：

```javascript
import TypePicker from './components/TypePicker.vue'
```

将原 `<section v-else-if="view === 'picker'">...</section>` 整段替换为：

```vue
<TypePicker v-else-if="view === 'picker'" @pick="pickType" @cancel="backHome" />
```

- [ ] **步骤 6：运行验证通过**

```bash
cd frontend && npm test
```

预期：3 passed。

- [ ] **步骤 7：Commit**

```bash
git add frontend/src/api.js frontend/src/components/TypePicker.vue frontend/tests/TypePicker.test.js frontend/src/App.vue
git commit -m "feat(frontend): API 客户端与 TypePicker 组件"
```

---

## 任务 11：PostForm 组件（必填校验 + 分支渲染）

**文件：**
- 创建：`frontend/src/components/PostForm.vue`
- 创建：`frontend/tests/PostForm.test.js`

- [ ] **步骤 1：写失败测试 `frontend/tests/PostForm.test.js`**

```javascript
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import PostForm from '../src/components/PostForm.vue'

describe('PostForm', () => {
  it('lost 类型只渲染联系方式文本框', () => {
    const w = mount(PostForm, { props: { postType: 'lost' } })
    expect(w.find('[data-testid="contact-options"]').exists()).toBe(false)
    expect(w.find('[data-testid="contact-detail"]').exists()).toBe(true)
  })

  it('found 类型渲染 3 个 contact_type 单选', () => {
    const w = mount(PostForm, { props: { postType: 'found' } })
    expect(w.find('[data-testid="contact-options"]').exists()).toBe(true)
    expect(w.findAll('[data-testid^="ct-"]').length).toBe(3)
  })

  it('未填必填项时点提交不会 emit submit', async () => {
    const w = mount(PostForm, { props: { postType: 'lost' } })
    await w.get('form').trigger('submit.prevent')
    expect(w.emitted().submit).toBeFalsy()
    expect(w.find('[data-testid="error"]').exists()).toBe(true)
  })

  it('lost 类型补齐字段后 emit submit 含 owner_contact', async () => {
    const w = mount(PostForm, { props: { postType: 'lost' } })
    await w.get('[data-testid="title"]').setValue('黑色雨伞')
    await w.get('[data-testid="category"]').setValue('daily')
    await w.get('[data-testid="location"]').setValue('B201')
    await w.get('[data-testid="event-time"]').setValue('2026-06-12T18:30')
    await w.get('[data-testid="contact-detail"]').setValue('微信 abc123')
    await w.get('form').trigger('submit.prevent')
    expect(w.emitted().submit).toBeTruthy()
    const payload = w.emitted().submit[0][0]
    expect(payload.contact_type).toBe('owner_contact')
    expect(payload.post_type).toBe('lost')
  })
})
```

- [ ] **步骤 2：运行验证失败**

```bash
cd frontend && npm test
```

预期：FAIL，找不到 `PostForm.vue`。

- [ ] **步骤 3：写 `frontend/src/components/PostForm.vue`**

```vue
<script setup>
import { ref, computed } from 'vue'

const props = defineProps({ postType: { type: String, required: true } })
const emit = defineEmits(['submit', 'cancel'])

const CATEGORIES = [
  ['electronics', '电子产品类'],
  ['id_card', '个人证件与卡类'],
  ['bag', '箱包与收纳'],
  ['accessory', '配饰'],
  ['clothing', '衣物'],
  ['daily', '日常小件'],
  ['study', '办公与学习'],
  ['sports', '运动与户外'],
  ['personal_care', '个人护理与健康'],
]

const FOUND_OPTIONS = [
  ['self_pickup', '自取'],
  ['contact', '联系方式'],
  ['handed_over', '已移交管理处'],
]

const title = ref('')
const category = ref('')
const location = ref('')
const eventTime = ref('')
const description = ref('')
const contactType = ref(props.postType === 'lost' ? 'owner_contact' : 'self_pickup')
const contactDetail = ref('')
const imageFile = ref(null)
const error = ref('')

const maxTime = computed(() => {
  const d = new Date()
  d.setSeconds(0, 0)
  return d.toISOString().slice(0, 16)
})

function onFile(e) {
  const f = e.target.files?.[0] || null
  if (!f) { imageFile.value = null; return }
  if (!['image/jpeg', 'image/png', 'image/webp'].includes(f.type)) {
    error.value = '图片必须是 jpg/png/webp'
    e.target.value = ''
    return
  }
  if (f.size > 5 * 1024 * 1024) {
    error.value = '图片不能超过 5MB'
    e.target.value = ''
    return
  }
  error.value = ''
  imageFile.value = f
}

function validate() {
  if (!title.value.trim()) return '请填写物品名称'
  if (title.value.length > 50) return '物品名称不能超过 50 字'
  if (!category.value) return '请选择物品种类'
  if (!location.value.trim()) return '请填写地点'
  if (!eventTime.value) return '请选择时间'
  if (!contactDetail.value.trim()) return '请填写联系方式描述'
  return ''
}

function onSubmit() {
  const msg = validate()
  if (msg) { error.value = msg; return }
  error.value = ''
  emit('submit', {
    post_type: props.postType,
    title: title.value,
    category: category.value,
    description: description.value || null,
    location: location.value,
    event_time: eventTime.value,
    contact_type: contactType.value,
    contact_detail: contactDetail.value,
    image: imageFile.value,
  })
}
</script>

<template>
  <form class="form" @submit.prevent="onSubmit">
    <h2>{{ postType === 'lost' ? '寻物帖' : '寻主帖' }}</h2>

    <label>物品名称 *
      <input data-testid="title" v-model="title" maxlength="50" required />
    </label>

    <label>物品种类 *
      <select data-testid="category" v-model="category" required>
        <option value="" disabled>请选择</option>
        <option v-for="[v, t] in CATEGORIES" :key="v" :value="v">{{ t }}</option>
      </select>
    </label>

    <label>物品图片
      <input type="file" accept="image/jpeg,image/png,image/webp" @change="onFile" />
    </label>

    <label>物品描述
      <textarea v-model="description" maxlength="500" rows="3" />
    </label>

    <label>{{ postType === 'lost' ? '丢失' : '捡到' }}地点 *
      <input data-testid="location" v-model="location" maxlength="100" required />
    </label>

    <label>{{ postType === 'lost' ? '丢失' : '捡到' }}时间 *
      <input data-testid="event-time" type="datetime-local" v-model="eventTime"
             :max="maxTime" required />
    </label>

    <fieldset v-if="postType === 'found'" data-testid="contact-options">
      <legend>联系方式 *</legend>
      <label v-for="[v, t] in FOUND_OPTIONS" :key="v">
        <input type="radio" :data-testid="`ct-${v}`" :value="v" v-model="contactType" />
        {{ t }}
      </label>
    </fieldset>

    <label>{{ postType === 'lost' ? '联系方式 *' : '具体描述 *' }}
      <textarea data-testid="contact-detail" v-model="contactDetail"
                maxlength="200" rows="2" required />
    </label>

    <p v-if="error" class="error" data-testid="error">{{ error }}</p>

    <div class="actions">
      <button type="submit" class="primary">提交</button>
      <button type="button" class="link" @click="emit('cancel')">取消</button>
    </div>
  </form>
</template>

<style scoped>
.form { display: flex; flex-direction: column; gap: 12px; padding: 16px 0; }
.form label { display: flex; flex-direction: column; gap: 4px; font-size: 14px; }
.form input, .form select, .form textarea {
  padding: 8px 10px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 14px;
}
fieldset { border: 1px solid #cbd5e1; border-radius: 6px; padding: 8px 12px; }
fieldset label { flex-direction: row; align-items: center; gap: 6px; }
.error { color: #dc2626; font-size: 14px; }
.actions { display: flex; gap: 12px; margin-top: 8px; }
.primary { background: #2563eb; color: white; border: 0; padding: 10px 20px;
  border-radius: 6px; cursor: pointer; }
.link { background: transparent; border: 0; color: #64748b; cursor: pointer; }
</style>
```

- [ ] **步骤 4：运行验证通过**

```bash
cd frontend && npm test
```

预期：6 passed（TypePicker 3 + PostForm 4，含已有 1 个 lost 默认 owner_contact 用例）。

- [ ] **步骤 5：Commit**

```bash
git add frontend/src/components/PostForm.vue frontend/tests/PostForm.test.js
git commit -m "feat(frontend): PostForm 组件（必填校验与分支渲染）"
```

---

## 任务 12：PostForm 接入 App.vue 与提交集成

**文件：**
- 修改：`frontend/src/App.vue`

- [ ] **步骤 1：完整替换 `frontend/src/App.vue`**

```vue
<script setup>
import { ref } from 'vue'
import TypePicker from './components/TypePicker.vue'
import PostForm from './components/PostForm.vue'
import { createPost } from './api.js'

const view = ref('home')
const postType = ref(null)
const submitting = ref(false)

function openPicker() { view.value = 'picker' }
function pickType(t) { postType.value = t; view.value = 'form' }
function backHome() { view.value = 'home'; postType.value = null }

async function onSubmit(payload) {
  submitting.value = true
  try {
    await createPost(payload)
    alert('发布成功')
    backHome()
  } catch (e) {
    const detail = e?.response?.data?.detail || '提交失败，请稍后重试'
    alert(detail)
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <main class="page">
    <header class="title">南哪寻宝</header>

    <section v-if="view === 'home'" class="home">
      <button class="primary" data-testid="btn-create" @click="openPicker">发帖</button>
    </section>

    <TypePicker v-else-if="view === 'picker'"
                @pick="pickType" @cancel="backHome" />

    <PostForm v-else
              :post-type="postType"
              @submit="onSubmit"
              @cancel="backHome" />
  </main>
</template>

<style>
:root { font-family: system-ui, -apple-system, "PingFang SC", sans-serif; }
.page { max-width: 640px; margin: 0 auto; padding: 32px 16px; }
.title { font-size: 24px; font-weight: 700; color: #0f172a; margin-bottom: 16px; }
.home { display: flex; justify-content: center; padding: 96px 0; }
.primary { background: #2563eb; color: white; border: 0; padding: 12px 20px;
  border-radius: 8px; font-size: 16px; cursor: pointer; }
.primary:hover { background: #1d4ed8; }
</style>
```

- [ ] **步骤 2：本地手动联调**（后端在 8000、前端 dev 5173）

```bash
# 终端 1
cd backend && uvicorn app.main:app --reload --port 8000
# 终端 2
cd frontend && npm run dev
```

打开 `http://localhost:5173`，走通 4 条用例（寻物 1 条无图、寻主 3 种 contact_type 各 1 条带图），全部 alert"发布成功"。

- [ ] **步骤 3：Commit**

```bash
git add frontend/src/App.vue
git commit -m "feat(frontend): 集成 PostForm 与提交流程"
```

---

## 任务 13：Dockerfile 与 docker-compose

**文件：**
- 创建：`backend/Dockerfile`
- 创建：`frontend/Dockerfile`
- 创建：`docker-compose.yml`

- [ ] **步骤 1：写 `backend/Dockerfile`**

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
RUN mkdir -p /app/uploads
ENV NJU_DB_URL=sqlite:////app/data/nju.db \
    NJU_UPLOAD_DIR=/app/uploads
EXPOSE 8000
CMD ["sh", "-c", "mkdir -p /app/data && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
```

- [ ] **步骤 2：写 `frontend/Dockerfile`**

```dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json ./
RUN npm install
COPY . .
RUN npm run build

FROM node:20-alpine
WORKDIR /app
RUN npm install -g serve
COPY --from=build /app/dist ./dist
EXPOSE 5173
CMD ["serve", "-s", "dist", "-l", "5173"]
```

- [ ] **步骤 3：写 `docker-compose.yml`**

```yaml
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend/uploads:/app/uploads
      - backend_data:/app/data
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')"]
      interval: 10s
      timeout: 3s
      retries: 5

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    depends_on:
      backend:
        condition: service_healthy

volumes:
  backend_data:
```

> 注：生产前端通过 `serve` 提供静态文件，API 请求走 `http://localhost:8000`（前端 build 产物里的相对 `/api` 在浏览器侧需 CORS 通；后端已开放 5173 来源）。

- [ ] **步骤 4：本地验证**

```bash
docker compose up --build
```

预期：两容器健康，访问 `http://localhost:5173` 可发帖；访问 `http://localhost:8000/api/health` 返回 `{"status":"ok"}`。

- [ ] **步骤 5：Commit**

```bash
git add backend/Dockerfile frontend/Dockerfile docker-compose.yml
git commit -m "build: 添加 Dockerfile 与 docker-compose 一键启动"
```

---

## 任务 14：CI、Makefile 与 README

**文件：**
- 创建：`Makefile`
- 创建：`.github/workflows/ci.yml`
- 修改：`README.md`

- [ ] **步骤 1：写 `Makefile`**

```makefile
.PHONY: test test-backend test-frontend dev build

test: test-backend test-frontend

test-backend:
	cd backend && pytest -v

test-frontend:
	cd frontend && npm test

dev:
	docker compose up --build

build:
	docker compose build
```

- [ ] **步骤 2：写 `.github/workflows/ci.yml`**

```yaml
name: CI

on:
  push:
  pull_request:

jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r backend/requirements.txt
      - run: cd backend && pytest -v

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
      - run: cd frontend && npm install
      - run: cd frontend && npm test
      - run: cd frontend && npm run build

  docker:
    runs-on: ubuntu-latest
    needs: [backend, frontend]
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - run: docker build -t nju-backend ./backend
      - run: docker build -t nju-frontend ./frontend
```

- [ ] **步骤 3：扩写 `README.md`**

```markdown
# 南哪寻宝（NJU LostFound）

南京大学失物招领与寻物启事平台。当前版本实现"发帖闭环"。

## 功能

- 首页一键发帖
- 寻物帖 / 寻主帖类型选择
- 9 类物品分类、单图上传、地点与时间记录
- 寻主帖支持 自取 / 联系方式 / 已移交管理处 三种交付方式

## 技术栈

后端 FastAPI + SQLite + SQLAlchemy；前端 Vue 3 + Vite + axios；测试 pytest + Vitest；容器化 Docker + docker-compose。

## 一键启动

\`\`\`bash
docker compose up --build
\`\`\`

- 前端：http://localhost:5173
- 后端 health：http://localhost:8000/api/health

## 本地开发

\`\`\`bash
# 后端
cd backend && python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# 前端
cd frontend && npm install && npm run dev
\`\`\`

## 测试

\`\`\`bash
make test
\`\`\`

## 目录结构

参见 [PLAN](docs/superpowers/plans/2026-06-13-post-creation-plan.md)。

## 文档

- [SPEC](docs/superpowers/specs/2026-06-13-post-creation-design.md)
- [PLAN](docs/superpowers/plans/2026-06-13-post-creation-plan.md)
- [AGENT_LOG](AGENT_LOG.md)
```

- [ ] **步骤 4：Commit**

```bash
git add Makefile .github/workflows/ci.yml README.md
git commit -m "ci: 添加 GitHub Actions、Makefile 与 README"
```

---

## 自检（writing-plans 内联）

- **规格覆盖度**：
  - SPEC §3.1 首页 → T9、T12 ✅
  - SPEC §3.2 类型选择 → T10 ✅
  - SPEC §3.3 表单 → T11、T12 ✅
  - SPEC §3.4 联系方式分支 → T5（后端跨字段校验）、T11（前端分支渲染） ✅
  - SPEC §6 数据模型 → T4 ✅
  - SPEC §7 API → T7、T8 ✅
  - SPEC §10 测试用例 → T3–T8、T10、T11 全部覆盖 ✅
  - SPEC §11 R2 孤儿图片 → T7 router 中 try/except 同步 `delete_image`（已在主路径任务实装，无需独立任务） ✅
  - SPEC §9 验收标准 1（compose up）→ T13 ✅
  - SPEC §9 验收标准 6（make test）→ T14 ✅
  - SPEC §9 验收标准 7（CI 三段式）→ T14 ✅
- **占位符扫描**：无 TODO；每个步骤都给出完整代码或精确命令。✅
- **类型一致性**：`PostCreate` / `PostType` / `Category` / `ContactType` / `PostOut` 命名贯穿 T5、T7；前端 `createPost(form)` 字段名与后端 `Form(...)` 一一对应；`data-testid` 在 T9、T10、T11 测试与组件中一致。✅

---

## 执行交接

计划已完成并保存到 `docs/superpowers/plans/2026-06-13-post-creation-plan.md`。两种执行方式：

1. **子代理驱动（推荐）** — 每个任务调度一个新的子代理，任务间进行审查，快速迭代
2. **内联执行** — 在当前会话中使用 executing-plans 执行任务，批量执行并设有检查点

**选哪种方式？**
