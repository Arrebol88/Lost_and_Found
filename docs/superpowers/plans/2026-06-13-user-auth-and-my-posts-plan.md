# 用户注册 / 登录与 "我的帖子" 实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 引入 `users` 表 + bcrypt + JWT 鉴权，把现有匿名 `X-Anon-Id` 体系全量替换；前端新增 `AuthDialog` 与 `我的帖子` tab；旧帖子/点赞/评论数据一次性清空。

**架构：** 后端新增 `app/auth/` 模块（jwt_utils + password + deps）与 `routers/auth.py`；`models.py` 把 `anon_id` 列替换为 `user_id` 并新增 `User` 模型；`database.init_db()` 在检测到旧 anon_id schema 时清空三张表 + uploads 目录。前端新增 `auth.js` 管理 token，axios 拦截器附 `Authorization`，新增 `AuthDialog.vue`；`App.vue` 改 hero + tabs；写操作前调用 `requireAuth(...)` 拦截。

**技术栈：** FastAPI、SQLAlchemy 1.4、`passlib[bcrypt]`、`PyJWT`；Vue 3 SFC + axios；测试 pytest + Vitest。

---

## 文件清单

新增（后端）：
- `backend/app/auth/__init__.py`
- `backend/app/auth/password.py`
- `backend/app/auth/jwt_utils.py`
- `backend/app/auth/deps.py`
- `backend/app/routers/auth.py`
- `backend/tests/test_auth.py`

修改（后端）：
- `backend/requirements.txt`（加 `passlib[bcrypt]==1.7.4`、`PyJWT==2.8.0`、`bcrypt==4.0.1`）
- `backend/app/models.py`、`backend/app/schemas.py`、`backend/app/database.py`、`backend/app/main.py`
- `backend/app/routers/posts.py`、`backend/app/routers/comments.py`
- `backend/tests/conftest.py`（新增 `auth_headers` fixture）
- `backend/tests/test_*.py`（每个用例改用 `auth_headers`）

新增（前端）：
- `frontend/src/auth.js`
- `frontend/src/components/AuthDialog.vue`
- `frontend/tests/auth.test.js`
- `frontend/tests/AuthDialog.test.js`

修改（前端）：
- `frontend/src/api.js`（axios 拦截器；删除 `ensureAnonId`）
- `frontend/src/App.vue`（hero 用户区、第三个 tab、写操作拦截）
- `frontend/src/components/PostDetail.vue`（写操作前 requireAuth；显示 author_username）
- `frontend/src/components/CommentList.vue`（显示 author_username）
- `frontend/tests/App.test.js`（少量增改）

---

### 任务 1：后端依赖与 User 模型

**文件：**
- 修改：`backend/requirements.txt`
- 修改：`backend/app/models.py`

- [ ] **步骤 1：写失败测试 `tests/test_auth.py::test_user_table_exists`**

```python
from sqlalchemy import inspect
from app.database import engine

def test_user_table_exists(client):
    insp = inspect(engine)
    cols = {c["name"] for c in insp.get_columns("users")}
    assert {"id", "username", "password_hash", "created_at"} <= cols
```

- [ ] **步骤 2：跑测试确认红**

`.\.venv\Scripts\python.exe -m pytest tests/test_auth.py::test_user_table_exists -q`  
预期：`NoSuchTableError: users` 或 `KeyError`。

- [ ] **步骤 3：依赖 + 模型实现**

`requirements.txt` 追加：

```
passlib[bcrypt]==1.7.4
bcrypt==4.0.1
PyJWT==2.8.0
```

`models.py` 增加：

```python
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(32), nullable=False, unique=True)
    password_hash = Column(String(128), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
```

- [ ] **步骤 4：安装依赖并跑测试**

`.\.venv\Scripts\python.exe -m pip install passlib[bcrypt]==1.7.4 bcrypt==4.0.1 PyJWT==2.8.0`  
`.\.venv\Scripts\python.exe -m pytest tests/test_auth.py -q` → PASS

- [ ] **步骤 5：Commit**

```bash
git add backend/requirements.txt backend/app/models.py backend/tests/test_auth.py
git commit -m "feat(auth): add user table and password deps"
```

---

### 任务 2：密码与 JWT 工具

**文件：**
- 创建：`backend/app/auth/__init__.py`（空）
- 创建：`backend/app/auth/password.py`
- 创建：`backend/app/auth/jwt_utils.py`

- [ ] **步骤 1：写失败测试 `tests/test_auth.py`**

```python
def test_password_hash_and_verify():
    from app.auth.password import hash_password, verify_password
    h = hash_password("hunter2")
    assert h != "hunter2"
    assert verify_password("hunter2", h) is True
    assert verify_password("wrong", h) is False


def test_jwt_round_trip():
    from app.auth.jwt_utils import create_token, decode_token
    t = create_token(user_id=42, username="alice")
    payload = decode_token(t)
    assert payload["sub"] == "42"
    assert payload["username"] == "alice"


def test_jwt_invalid():
    from app.auth.jwt_utils import decode_token, JwtError
    import pytest
    with pytest.raises(JwtError):
        decode_token("not-a-token")
```

- [ ] **步骤 2：跑测试确认红**

`pytest tests/test_auth.py -q` → 3 个新增 fail。

- [ ] **步骤 3：实现 `password.py`**

```python
from passlib.context import CryptContext

_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    return _ctx.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return _ctx.verify(plain, hashed)
```

- [ ] **步骤 4：实现 `jwt_utils.py`**

```python
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
```

- [ ] **步骤 5：跑测试 → PASS + Commit**

```bash
git add backend/app/auth/
git commit -m "feat(auth): add password and jwt helpers"
```

---

### 任务 3：`get_current_user` 依赖 + 路由 `/api/auth/*`

**文件：**
- 创建：`backend/app/auth/deps.py`
- 创建：`backend/app/routers/auth.py`
- 修改：`backend/app/main.py`（include_router）
- 修改：`backend/app/schemas.py`

- [ ] **步骤 1：写失败测试**

```python
def _register(client, username="alice", password="hunter2"):
    return client.post("/api/auth/register", json={"username": username, "password": password})


def test_register_returns_token(client):
    r = _register(client)
    assert r.status_code == 201
    body = r.json()
    assert body["user"]["username"] == "alice"
    assert isinstance(body["token"], str) and len(body["token"]) > 20


def test_register_duplicate_username(client):
    _register(client)
    r = _register(client)
    assert r.status_code == 409


def test_register_validation(client):
    r = client.post("/api/auth/register", json={"username": "ab", "password": "hunter2"})
    assert r.status_code == 422


def test_login_success_and_failure(client):
    _register(client)
    ok = client.post("/api/auth/login", json={"username": "alice", "password": "hunter2"})
    assert ok.status_code == 200
    bad = client.post("/api/auth/login", json={"username": "alice", "password": "wrong"})
    assert bad.status_code == 401


def test_me_requires_auth(client):
    no = client.get("/api/auth/me")
    assert no.status_code == 401
    token = _register(client).json()["token"]
    yes = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert yes.status_code == 200
    assert yes.json()["username"] == "alice"
```

- [ ] **步骤 2：跑测试确认红**

`pytest tests/test_auth.py -q` → 5 个新增 fail。

- [ ] **步骤 3：实现 schemas**

```python
class RegisterIn(BaseModel):
    username: str = Field(..., min_length=3, max_length=32, pattern=r"^[\w\u4e00-\u9fa5]+$")
    password: str = Field(..., min_length=6, max_length=128)


class LoginIn(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    model_config = {"from_attributes": True}


class TokenOut(BaseModel):
    token: str
    user: UserOut
```

- [ ] **步骤 4：实现 `auth/deps.py`**

```python
from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app import models
from app.database import get_db
from app.auth.jwt_utils import decode_token, JwtError


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
```

- [ ] **步骤 5：实现 `routers/auth.py`**

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models
from app.database import get_db
from app.schemas import RegisterIn, LoginIn, TokenOut, UserOut
from app.auth.password import hash_password, verify_password
from app.auth.jwt_utils import create_token
from app.auth.deps import get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.username.ilike(payload.username)).first()
    if existing:
        raise HTTPException(status_code=409, detail="用户名已被占用")
    user = models.User(username=payload.username, password_hash=hash_password(payload.password))
    db.add(user); db.commit(); db.refresh(user)
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
```

- [ ] **步骤 6：`main.py` 注册路由**

```python
from app.routers import posts, comments, auth as auth_router
app.include_router(auth_router.router)
```

- [ ] **步骤 7：跑测试 → PASS + Commit**

```bash
git add backend/app/schemas.py backend/app/auth/deps.py backend/app/routers/auth.py backend/app/main.py
git commit -m "feat(auth): add register, login, me endpoints"
```

---

### 任务 4：数据库迁移与 anon_id → user_id

**文件：**
- 修改：`backend/app/models.py`、`backend/app/database.py`、`backend/app/schemas.py`

- [ ] **步骤 1：写失败测试**

```python
def test_post_has_user_id_column(client):
    from sqlalchemy import inspect
    from app.database import engine
    cols = {c["name"] for c in inspect(engine).get_columns("posts")}
    assert "user_id" in cols
    assert "anon_id" not in cols


def test_post_likes_user_id(client):
    from sqlalchemy import inspect
    from app.database import engine
    cols = {c["name"] for c in inspect(engine).get_columns("post_likes")}
    assert "user_id" in cols
```

- [ ] **步骤 2：跑测试确认红**

- [ ] **步骤 3：models.py**

把 `anon_id = Column(String(36))` 替换为 `user_id = Column(Integer, ForeignKey("users.id"), nullable=False)`，并对 `Post / PostLike / PostComment` 一并修改。

- [ ] **步骤 4：database.py 添加一次性清表逻辑**

```python
def init_db() -> None:
    global engine, SessionLocal
    db_url = os.getenv("NJU_DB_URL", "sqlite:///./nju_lostfound.db")
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    from app import models  # noqa: F401
    _purge_legacy_anon_schema()
    Base.metadata.create_all(bind=engine)


def _purge_legacy_anon_schema() -> None:
    from sqlalchemy import inspect, text
    insp = inspect(engine)
    if "posts" not in insp.get_table_names():
        return
    cols = {c["name"] for c in insp.get_columns("posts")}
    if "anon_id" not in cols:
        return
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS post_comments"))
        conn.execute(text("DROP TABLE IF EXISTS post_likes"))
        conn.execute(text("DROP TABLE IF EXISTS posts"))
    upload_dir = os.getenv("NJU_UPLOAD_DIR", "./uploads")
    if os.path.isdir(upload_dir):
        import shutil
        for entry in os.listdir(upload_dir):
            shutil.rmtree(os.path.join(upload_dir, entry), ignore_errors=True)
```

- [ ] **步骤 5：schemas.py**

`PostOut` 添加 `author_username: str`，`PostDetailOut.mine` 保留；`CommentOut` 添加 `author_username: str`。

- [ ] **步骤 6：跑测试 → PASS + Commit**

```bash
git add backend/app/models.py backend/app/database.py backend/app/schemas.py
git commit -m "refactor(db): migrate anon_id to user_id and purge legacy"
```

---

### 任务 5：conftest auth_headers + 改造现有 60 测试

**文件：**
- 修改：`backend/tests/conftest.py`
- 修改：`backend/tests/test_post_*.py`、`test_posts_*.py`

- [ ] **步骤 1：实现 fixture**

```python
@pytest.fixture
def auth():
    used = {}
    def _make(client, username="alice", password="hunter2"):
        if username in used:
            return used[username]
        client.post("/api/auth/register", json={"username": username, "password": password})
        r = client.post("/api/auth/login", json={"username": username, "password": password})
        token = r.json()["token"]
        used[username] = {"Authorization": f"Bearer {token}"}
        return used[username]
    return _make
```

- [ ] **步骤 2：批量替换**

将所有 `headers={"X-Anon-Id": ANON}` 替换为 `headers=auth(client, "alice")`；保留两个用户的隔离场景（`alice` / `bob`）。删除 `ANON_A / ANON_B / ANON / _UUID_RE` 等常量。

- [ ] **步骤 3：跑全后端测试 → PASS**

`pytest -q`，预期 `60+ passed`。

- [ ] **步骤 4：Commit**

```bash
git add backend/tests/
git commit -m "test(auth): migrate fixtures from anon_id to bearer"
```

---

### 任务 6：posts.py / comments.py 切换到 get_current_user

**文件：** `backend/app/routers/posts.py`、`backend/app/routers/comments.py`

- [ ] **步骤 1：替换依赖**

把 `anon_id: str = Depends(get_anon_id)` 替换为 `current: models.User = Depends(get_current_user)`；列表 / 详情接口（GET）改成 `Optional[models.User] = Depends(get_current_user_optional)`。

- [ ] **步骤 2：mine 计算 + author_username 注入**

序列化时 `author_username = post.author.username`（用 `relationship`），`mine = current is not None and current.id == post.user_id`。

- [ ] **步骤 3：列表新增 mine 参数**

```python
@router.get("/posts")
def list_posts(
    post_type: Optional[str] = None,
    mine: Optional[bool] = False,
    ...,
    current: Optional[models.User] = Depends(get_current_user_optional),
):
    if mine and current is None:
        raise HTTPException(401, detail="未登录")
    q = db.query(models.Post)
    if mine:
        q = q.filter(models.Post.user_id == current.id)
    elif post_type:
        q = q.filter(models.Post.post_type == post_type)
    ...
```

- [ ] **步骤 4：跑全测试 → PASS + Commit**

```bash
git add backend/app/routers/posts.py backend/app/routers/comments.py
git commit -m "feat(posts): switch authentication to bearer token"
```

---

### 任务 7：前端 auth.js + axios 拦截器

**文件：**
- 创建：`frontend/src/auth.js`
- 修改：`frontend/src/api.js`
- 创建：`frontend/tests/auth.test.js`

- [ ] **步骤 1：写失败测试 `tests/auth.test.js`**

```javascript
import { describe, it, expect, beforeEach } from 'vitest'
import { setSession, getToken, currentUser, logout } from '../src/auth.js'

describe('auth session store', () => {
  beforeEach(() => { localStorage.clear(); logout() })

  it('设置 session 后返回 token 与 user', () => {
    setSession('tk', { id: 1, username: 'alice' })
    expect(getToken()).toBe('tk')
    expect(currentUser.value).toEqual({ id: 1, username: 'alice' })
  })

  it('logout 清空 token 与 user', () => {
    setSession('tk', { id: 1, username: 'a' })
    logout()
    expect(getToken()).toBe(null)
    expect(currentUser.value).toBe(null)
  })
})
```

- [ ] **步骤 2：实现 `auth.js`**

```javascript
import { ref } from 'vue'

const TOKEN_KEY = 'nju_token'
const USER_KEY = 'nju_user'

export const currentUser = ref(JSON.parse(localStorage.getItem(USER_KEY) || 'null'))

export function getToken() {
  return localStorage.getItem(TOKEN_KEY) || null
}

export function setSession(token, user) {
  localStorage.setItem(TOKEN_KEY, token)
  localStorage.setItem(USER_KEY, JSON.stringify(user))
  currentUser.value = user
}

export function logout() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
  currentUser.value = null
}
```

- [ ] **步骤 3：改 `api.js`**

- 删除 `ensureAnonId` 与所有 `X-Anon-Id` 注入。
- axios 实例上加 request 拦截器：若 `getToken()` 非空则附 `Authorization`。
- 加 response 拦截器：401 时调用 `logout()` 并 reject。
- 新增 `register / login / fetchMe / listMyPosts`。

- [ ] **步骤 4：跑测试 → PASS + Commit**

```bash
git add frontend/src/auth.js frontend/src/api.js frontend/tests/auth.test.js
git commit -m "feat(frontend): bearer token session store"
```

---

### 任务 8：AuthDialog.vue

**文件：**
- 创建：`frontend/src/components/AuthDialog.vue`
- 创建：`frontend/tests/AuthDialog.test.js`

- [ ] **步骤 1：写测试**

```javascript
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import AuthDialog from '../src/components/AuthDialog.vue'
import { register as apiRegister, login as apiLogin } from '../src/api.js'

vi.mock('../src/api.js', () => ({
  register: vi.fn(),
  login: vi.fn(),
}))

describe('AuthDialog', () => {
  beforeEach(() => { apiRegister.mockReset(); apiLogin.mockReset() })

  it('登录成功后 emit success', async () => {
    apiLogin.mockResolvedValue({ token: 'tk', user: { id: 1, username: 'alice' } })
    const w = mount(AuthDialog)
    await w.get('[data-testid="auth-username"]').setValue('alice')
    await w.get('[data-testid="auth-password"]').setValue('hunter2')
    await w.get('[data-testid="auth-submit"]').trigger('click')
    await flushPromises()
    expect(apiLogin).toHaveBeenCalledWith('alice', 'hunter2')
    expect(w.emitted().success[0][0].user.username).toBe('alice')
  })

  it('切换到注册 tab 后调用 register', async () => {
    apiRegister.mockResolvedValue({ token: 'tk', user: { id: 1, username: 'bob' } })
    const w = mount(AuthDialog)
    await w.get('[data-testid="auth-tab-register"]').trigger('click')
    await w.get('[data-testid="auth-username"]').setValue('bob')
    await w.get('[data-testid="auth-password"]').setValue('hunter2')
    await w.get('[data-testid="auth-submit"]').trigger('click')
    await flushPromises()
    expect(apiRegister).toHaveBeenCalledWith('bob', 'hunter2')
  })
})
```

- [ ] **步骤 2：实现组件**

模态框样式遵循 `tokens.css`：暖灰底 + surface 卡片；含 `登录` `注册` 两 tab；提交按钮 disabled 直到用户名/密码非空。

- [ ] **步骤 3：跑测试 → PASS + Commit**

```bash
git add frontend/src/components/AuthDialog.vue frontend/tests/AuthDialog.test.js
git commit -m "feat(frontend): add auth dialog"
```

---

### 任务 9：App.vue hero 用户区 + 我的帖子 tab

**文件：** `frontend/src/App.vue`、`frontend/tests/App.test.js`

- [ ] **步骤 1：写测试增量**

```javascript
it('未登录点 我要发帖 弹出 AuthDialog', async () => {
  const w = mount(App)
  await flushPromises()
  await w.get('[data-testid="btn-create"]').trigger('click')
  expect(w.findComponent({ name: 'AuthDialog' }).exists()).toBe(true)
})

it('登录后切到 我的帖子 tab 调 listPosts mine=true', async () => {
  const { setSession } = await import('../src/auth.js')
  setSession('tk', { id: 1, username: 'alice' })
  listPosts.mockResolvedValue([])
  const w = mount(App)
  await flushPromises()
  await w.get('[data-testid="tab-mine"]').trigger('click')
  await flushPromises()
  expect(listPosts).toHaveBeenLastCalledWith(expect.objectContaining({ mine: true }))
})
```

- [ ] **步骤 2：改 App.vue**

- 引入 `currentUser, logout` from `auth.js`、`AuthDialog`。
- Hero 右侧根据 `currentUser` 切显示。
- Tabs 增加 `data-testid="tab-mine"`，选中态时 `loadPosts` 切走 `post_type` 改传 `mine: true`。
- `loadPosts` 内：`if (activeTab.value === 'mine') return listPosts({ mine: true, ...filters.value })`。
- 写操作 `openPicker`：未登录则 `authDialog.value = true`；登录后行为不变。

- [ ] **步骤 3：跑测试 → PASS + Commit**

```bash
git add frontend/src/App.vue frontend/tests/App.test.js
git commit -m "feat(frontend): hero user area and my posts tab"
```

---

### 任务 10：详情页 / 评论的作者展示与登录拦截

**文件：** `frontend/src/components/PostDetail.vue`、`frontend/src/components/CommentList.vue`、相关测试

- [ ] **步骤 1：CommentList 显示 author_username**

```vue
<p class="meta">
  <span>{{ c.author_username }}</span>
  <span class="dot">·</span>
  <span>{{ fmt(c.created_at) }}</span>
</p>
```

- [ ] **步骤 2：PostDetail 显示作者**

`meta` 行多渲染 `<span>作者：{{ post.author_username }}</span>`。

- [ ] **步骤 3：写操作前置鉴权**

`onLike / onSubmitComment / onDeleteComment / onEdit / onDeletePost` 在调用 API 前用 `if (!currentUser.value) { emit('require-auth'); return }`。`App.vue` 监听 `require-auth` 弹 `AuthDialog`。

- [ ] **步骤 4：跑全前端测试 → PASS + Commit**

`npm test --silent && npm run build --silent`

```bash
git add frontend/src/components/PostDetail.vue frontend/src/components/CommentList.vue
git commit -m "feat(frontend): show author and gate writes by login"
```

---

### 任务 11：文档与全量验证

**文件：** `README.md`、`AGENT_LOG.md`、SPEC §11 自评（非必须）

- [ ] **步骤 1：README 加用户系统说明**

在"功能"段添一行 "用户注册 / 登录 / 我的帖子"；在"环境变量"段补 `JWT_SECRET`。

- [ ] **步骤 2：AGENT_LOG 追加段**

记录本次 11 个 commit 的目的与本任务所属技能链。

- [ ] **步骤 3：全量验证**

```
backend  : pytest -q          → 期望 ≥ 60 passed（含新增 auth 用例）
frontend : npm test --silent  → 期望 ≥ 38 + 新增用例 passed
frontend : npm run build      → 成功
docker compose build          → 成功（如可用）
```

- [ ] **步骤 4：Commit**

```bash
git add README.md AGENT_LOG.md
git commit -m "docs: record user auth and my posts"
```

---

## 依赖关系

- T1 → T2 → T3：依赖链严格。
- T4 必须在 T6 之前（schemas 与 models 改完才能动 router）。
- T5 在 T4/T6 之间穿插（fixtures 调整后 T6 才能通过全测试）。
- T7 必须在 T8/T9 之前（前端 token 模块）。
- T8 在 T9 之前（App 引用 AuthDialog）。
- T10 依赖 T9（前端 require-auth 事件链）。
- T11 必须最后。

## 自检备注

- 占位符：无 TODO；所有步骤都给出代码或精确命令。
- 类型一致：`User.id` 全链路 int；`token` 全链路 string；`mine` boolean。
- 范围：单一规格可覆盖，无需拆子项目。
