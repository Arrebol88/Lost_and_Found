# 冷启动验证包：用户系统 T2「密码与 JWT 工具」

> **用途**：把整个文件投喂给一个**全新的 Cursor Agent 会话**（不要让它读取仓库其它文件，也不要补充任何口头解释）。  
> **目标**：让 Cursor 仅凭 SPEC + PLAN 自主完成 Task 2 的 TDD 红→绿，并暴露 SPEC 的隐性假设。  
> **预期耗时**：1–1.5 小时。  
> **完成后**：把整段 Cursor 对话原文（含它的提问与最终改动）粘回来，由主开发 agent 整理进 `SPEC_PROCESS.md`。

---

## A. 系统/首条 prompt（直接复制给 Cursor）

```
你是一个独立工作的实现工程师。当前是一个全新会话，你不能读到任何此前的对话历史。

我会向你提供一份设计文档（SPEC）和一份实现计划（PLAN）的相关章节。请仅依据这两份文档，完成 PLAN 中的「任务 2：密码与 JWT 工具」。

工作纪律：
1. 严格遵循 TDD：先写出会失败的测试，运行测试看到红色，再写最少代码使它们变绿。
2. 颗粒度对齐 PLAN 中的步骤号；每完成一个步骤都给出对应的 git diff 摘要。
3. 遇到任何不明确、含糊、自相矛盾、文档没明说但你不得不做选择的地方，**立刻停下来用一个明确的问题问我**，不要凭猜测继续。
4. 不要扩展 task 范围；不要重构无关代码；不要新增依赖（除非 SPEC/PLAN 明确允许）。
5. 你的工作目录是一个干净的 Python 后端工程：`backend/app/` 已有基础包结构，`backend/tests/` 已存在 conftest，`requirements.txt` 已有 fastapi、pytest 等基础依赖。本任务允许新增 `passlib[bcrypt]==1.7.4`、`bcrypt==4.0.1`、`PyJWT==2.8.0`。

每一轮回复请按以下格式：
- 「我理解的目标」一句话
- 「我准备做的下一步」三行内
- 「需要确认的疑问（如果有）」编号列出

确认收到，请回 OK 并复述任务编号与你将要写的第一个失败测试名称。
```

---

## B. 给 Cursor 的 SPEC 摘录（仅 §1 / §2 / §3.1–§3.3 / §4 安全段落 + 任务 2 描述）

### 1. 问题陈述

现有项目所有写操作依赖 `localStorage` 中的 `X-Anon-Id`（随机 UUID），导致换浏览器即丢身份、可伪造、无认证强度。本期改造为「用户名 + 密码 + JWT」体系。

### 3.1 注册 `POST /api/auth/register`

- 入参：`{ username: str, password: str }`
- `username`：3–32 字符，允许字母 / 数字 / 下划线 / 汉字；查重不区分大小写。
- `password`：≥ 6 字符，前后不去空格。
- 成功：写入 `users` 表（**bcrypt 哈希**），返回 `{ token, user: { id, username } }`，HTTP 201。
- 失败：用户名重复 409；格式不合法 422。

### 3.2 登录 `POST /api/auth/login`

- 校验 bcrypt 密码匹配，统一文案"用户名或密码错误"，HTTP 401（**不暴露用户存在性**）。
- 成功 200，返回结构同注册。

### 3.3 当前用户 `GET /api/auth/me`

- 必须登录；返回 `{ id, username }`，HTTP 200。
- 缺 token / token 非法 / 过期 → 401。

### 4. 非功能性需求（节选）

- **安全**：bcrypt 哈希；JWT HS256，密钥从 `JWT_SECRET` 环境变量读取，缺失时使用本地默认值（仅开发用）；token 有效期 7 天；不实现 refresh。
- **可观测性**：401/409 在响应体的 `detail` 字段返回中文文案。

---

## C. 给 Cursor 的 PLAN 摘录（仅任务 2）

### 任务 2：密码与 JWT 工具

**文件：**
- 创建：`backend/app/auth/__init__.py`（空）
- 创建：`backend/app/auth/password.py`
- 创建：`backend/app/auth/jwt_utils.py`

**步骤 1：写失败测试 `tests/test_auth.py`**

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

**步骤 2：跑测试确认红**

`pytest tests/test_auth.py -q` → 3 个新增 fail。

**步骤 3：实现 `password.py`**

参考骨架：

```python
from passlib.context import CryptContext

_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    return _ctx.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return _ctx.verify(plain, hashed)
```

**步骤 4：实现 `jwt_utils.py`**

参考骨架：

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

**步骤 5：跑测试 → PASS + Commit**

```bash
git add backend/app/auth/
git commit -m "feat(auth): add password and jwt helpers"
```

---

## D. 验证记录回收清单（你跑完 Cursor 之后填）

为方便后续整理，请用以下 4 段标题回贴对话：

```
## 1. Cursor 第一轮"复述 + 提问"原文
（粘贴）

## 2. Cursor 在执行过程中提出的所有澄清问题（按时间顺序）
（粘贴）

## 3. Cursor 最终产出的 password.py / jwt_utils.py / test_auth.py（git diff 或全文）
（粘贴）

## 4. Cursor 跑出的 pytest 输出（红→绿两次）
（粘贴）
```

我会据此填写 `SPEC_PROCESS.md` 的"冷启动验证"章节，并对 SPEC 做修订（如有必要）。

---

## E. 操作步骤清单

1. 在仓库根开一个新 worktree 给冷启动 agent，避免污染主线：
   ```powershell
   git worktree add .worktrees/cold-start -b cold-start/cursor-t2 main
   ```
2. 打开 Cursor，**新开一个完全空的 Composer / Agent 会话**（不加载任何 rules、不引入这条 worktree 之外的文件）。
3. 把上面的 **A**、**B**、**C** 三段拼成一条 prompt 一次性发给 Cursor。
4. 让它独立工作 1–1.5 小时；遇到它"凭猜测继续"时拍它停下来；它合理的提问按 SPEC 真实意思回答（**不要超出 SPEC 范围**——SPEC 没说的就如实告诉它"SPEC 没规定，请你假设并明示假设"）。
5. 全部跑完后把 4 段对话回贴到主会话，我整理。
