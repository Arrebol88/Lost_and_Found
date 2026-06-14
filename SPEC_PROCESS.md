# SPEC_PROCESS.md — 与 Superpowers 协作生成 SPEC 与 PLAN 的过程文档

> 本文件按照《AI4SE 期末项目》§4.4 的要求，记录与主智能体（Trae 内 Claude）以 Superpowers `brainstorming` / `writing-plans` 协作时的关键节点、关键迭代、AI 建议的采纳与推翻；并按 §4.5 完成"冷启动验证"。

仓库：<https://github.com/Arrebol88/Lost_and_Found>

---

## 1. 总览

本项目共启动了 **6 期 SPEC + PLAN**，覆盖发帖、列表筛选、详情交互、编辑/删除、Open Design 视觉重构、用户系统。每一期都遵循同一个流程：

```
brainstorming → 用户分块签字 → SPEC.md → writing-plans → PLAN.md
        ↓                                              ↓
        4–7 轮关键澄清问题                              10 个左右 TDD 任务
```

完整产出：

| 期 | SPEC | PLAN |
|---|---|---|
| 发帖 | `docs/superpowers/specs/2026-06-13-post-creation-design.md` | `docs/superpowers/plans/2026-06-13-post-creation-plan.md` |
| 列表 / 筛选 | `2026-06-13-post-listing-filters-design.md` | `2026-06-13-post-listing-filters-plan.md` |
| 详情 / 交互 | `2026-06-13-post-detail-interactions-design.md` | `2026-06-13-post-detail-interactions-plan.md` |
| 编辑 / 删除 | `2026-06-13-post-edit-delete-design.md` | `2026-06-13-post-edit-delete-plan.md` |
| 视觉重构 | `2026-06-13-open-design-visual-refresh.md` | `2026-06-13-open-design-visual-refresh-plan.md` |
| 用户系统 | `2026-06-13-user-auth-and-my-posts.md` | `2026-06-13-user-auth-and-my-posts-plan.md` |

---

## 2. brainstorming 关键节点（精选）

> 选取三期 brainstorming 中"AI 主动追问"和"由此引发设计变化"的代表性节点。

### 2.1 发帖（第 1 期）

| 序号 | AI 追问 | 我的回答 | 设计变化 |
|---|---|---|---|
| Q1 | "loss/found 两类帖子在'联系方式'语义上一致吗？" | 不一致：丢失帖填失主联系方式，拾得帖可选自取/联系/已交管理处 | SPEC 增加 `contact_type` 枚举，并加 `model_validator` 强制 `lost ↔ owner_contact`、`found ↔ self_pickup/contact/handed_over` |
| Q2 | "图片是必填吗？大小上限？格式？" | 选填；≤ 5 MB；jpg/png/webp | 衍生出 magic bytes 校验（避免改后缀绕过） |


### 2.2 列表与筛选（第 2 期）

| 序号 | AI 追问 | 我的回答 | 设计变化 |
|---|---|---|---|
| Q5 | "列表返回是否带 `contact_detail`？这是隐私字段。" | 不带 | `PostListItem` 与 `PostOut` 分离，列表只暴露摘要字段 |

**反思**：Q5 让我意识到"列表 schema ≠ 详情 schema"。AI 在隐私边界上比我更敏感。

### 2.3 用户系统（第 6 期）

| 序号 | AI 追问 | 我的回答 | 设计变化 |
|---|---|---|---|
| Q6 | "JWT vs Session vs 仅用户名前端 fake？" | JWT | 后端无状态，与原 `X-Anon-Id` header 模式同构，迁移成本低 |
| Q7 | "历史 anon_id 数据如何处理？" | **全部清空** | `database.init_db()` 检测到旧 schema 时 DROP 三张表 + 清 uploads；测试 fixture 同步重做 |
| Q8 | "未登录可看吗？我的帖子 tab 放哪？" | 可看；tab 与寻物/寻主同级；未登录占位 | 浏览门槛低、转化路径短 |

**反思**：Q7 是最大的"成本/价值"权衡。AI 默认会给"兼容历史 anon_id 数据"的 C 方案（绑定/认领），但工作量翻倍且没有作业价值，我直接选 B"清空"。

---

## 3. 至少 3 轮关键迭代节选

### 迭代 A：发帖的"联系方式"语义（第 1 期 Q1）

**修订前 SPEC（草稿）**：

```
contact_type: 自取 / 联系方式 / 已交管理处
```

**AI 反问**：
> "丢失帖（lost）也能选'已交管理处'吗？语义上似乎只对拾得帖有效。"

**我的处理**：在 SPEC 第 3 章"功能规约"加入 `contact_type` 枚举的硬约束矩阵：

```
post_type=lost  → contact_type ∈ { owner_contact }
post_type=found → contact_type ∈ { self_pickup, contact, handed_over }
```

**修订后**：后端 `PostCreate` 改为 `model_validator(mode='after')`，前端 `PostForm.vue` 根据 `post_type` 动态渲染候选；测试新增 `test_create_post_rejects_lost_with_self_pickup`。

---


### 迭代 B：用户系统的密码强度

**AI 初始提议**：B 方案（≥ 8 位且字母 + 数字）。

**我的反问**：

> "B 严格的好处是什么？是否会拖累注册转化？"

**AI 给出对比**：

| 维度 | A 宽松 (≥6) | B 严格 (≥8 + 复合) |
|---|---|---|
| 安全 | 中 | 高 |
| 注册流畅度 | 高 | 低 |
| 课业演示 | 够用 | 浪费 UX 时间 |

**我的处理**：选 A 宽松。理由："安全 vs UX" 在校园场景下倾斜到 UX，并将"扩展密码强度"列入"未来工作"。

---

### 迭代 C：注册校验失败的"用户可见性"

**触发**：用户系统第 6 期上线后第一次实际试用，浏览器控制台报 `POST /api/auth/register 422 Unprocessable Entity`，但页面只看到一行没头没脑的"注册失败"红字。

**修订前 SPEC**（用户系统 §3.1）：

```
- username: 3–32 字符，允许字母 / 数字 / 下划线 / 汉字；查重不区分大小写。
- password: ≥ 6 字符，前后不去空格。
- 失败：用户名重复 409；格式不合法 422。
```

**问题暴露**：SPEC 把"HTTP code"写到位了（422 + 409），但**没有规定"用户在界面上看到什么"**。AI 落实时严格遵守 SPEC 字面：

- 后端：用 Pydantic `Field(pattern=..., min_length=...)` 直接校验，错误时 FastAPI 自动返回 `detail` 字段——但这个字段是 **数组**（`[{loc, msg, type, ...}]`），不是字符串。
- 前端：`AuthDialog` 的错误处理写的是 `typeof detail === 'string' ? detail : '注册失败'`，于是 422 永远走到笼统兜底文案。

**我的处理**：要求 AI 在不修后端的前提下：

1. **前端预校验**：在前端用相同的正则 + 长度规则先做一遍校验，按钮在不合规时灰掉，禁止把不合规请求发出去。
2. **22 数组型 detail 解析**：写 `formatDetail()` 把 `loc` 末尾是 `username` / `password` 的错误转成中文文案"用户名不合法：…" / "密码不合法：…"。
3. **`<form @submit.prevent>` 包装**：消除 Chromium 的 "Password field is not contained in a form" 警告。

**反过来对 SPEC 做的修订**（已写入 [SPEC_PROCESS §5.4 F1–F4](#54-修订前后的-spec--plan-关键-diff)）：

```diff
@@ §3.1 注册的"失败"小节
- - 失败：用户名重复 409；格式不合法 422。
+ - 失败：用户名重复 409；格式不合法 422。
+   - **用户可见性约定**：失败响应必须能被前端解析成具体中文文案——
+     - 422 detail 数组中 `loc` 末尾为 `username` / `password` 的项要展开到对话框；
+     - 前端必须做与后端同规则的预校验，避免把可预防的请求发出去；
+     - 不允许出现笼统的"注册失败"兜底文案。
```

**意义**：这是项目里最有教学价值的一次迭代。AI 严格按 SPEC 实现，没有任何"违规"——但用户实际用起来体感是错的。**SPEC 的"错误处理"一节不能只列 HTTP code，必须连带规定"用户在 UI 上看到什么"**。这条经验已被反向用在 [REFLECTION §4](REFLECTION.md) 里作为"SPEC 写得不够细导致小翻车"的案例。

---

## 4. AI 建议的采纳 / 推翻清单

| 类别 | 我采纳 | 我推翻或修正 |
|---|---|---|
| **架构** | 后端按 `routers/` 分模块；前端 `auth.js` 单例；axios 拦截器；模型加 `relationship` 自动 join | 拒绝引入 ORM 迁移工具（Alembic）——一次性清表更简单；拒绝 OD MCP 路线 |
| **测试** | TDD 红→绿严格执行；用 `tmp_path` 隔离每个 test 的 SQLite 与 uploads；前端 `vi.mock('../src/auth.js')` 用 `async () => { const { ref } = await import('vue') }` 模式以兼容 hoist | 拒绝在视觉重构期补"视觉回归测试"——成本太高 |
| **设计** | Notion 暖灰调；token 化色板与字号节奏；P0/P1/P2 清单 | 拒绝亮 + 暗双主题；拒绝引入图标字体库；拒绝插画 |
| **范围** | 严格按 SPEC，不主动扩展 scope | 多次拒绝 AI 的"顺手再做一下…"提议（搜索、状态流转、admin 后台）——留作下一轮 |

---

## 5. 冷启动验证（§4.5）

> 主开发 agent：Trae 内 Claude  
> 验证 agent：**Cursor**（Composer / Agent 模式）  
> 选定 task：**用户系统 PLAN 的任务 2 — 密码与 JWT 工具**（纯函数 + 单元测试，最容易暴露 spec 漏洞）  
> 执行包：[`docs/superpowers/cold-start/cold-start-package.md`](superpowers/cold-start/cold-start-package.md)  
> worktree：`.worktrees/cold-start`  分支 `cold-start/cursor-t2`

### 5.1 Cursor 在哪些地方停下来问了问题？

Cursor 第一轮"复述 + 提问"原文：

> 我理解的目标：仅依据 SPEC 和 PLAN，完成任务 2「密码与 JWT 工具」，并严格按 TDD 先写失败测试再实现最少代码。
>
> 我准备做的下一步：先创建 `tests/test_auth.py` 中的第一个失败测试。
>
> 我将先写的第一个失败测试名称：`test_password_hash_and_verify`

执行过程中，Cursor 实际上**没有提出任何澄清问题**就直接走完了 TDD 红→绿。

| 问题 | 暴露的 SPEC 缺陷 | 是 spec 写错了 还是它读错了 |
|---|---|---|
| —（无） | —（针对本 task）SPEC + PLAN 节选已足够明确，cold-start agent 没有遇到模糊处 | — |

**值得反思的事**：Cursor 没问问题，本身是双刃信号——

- **正面**：SPEC §3.1–§4 + PLAN 任务 2 把字段、HTTP code、bcrypt + JWT HS256 + 7 天过期 + `JWT_SECRET` fallback 这些边界写到位了，新代理凭文档就能复现实现。
- **风险**：也可能 Cursor 错过了某个隐性假设（例如 token 密钥默认值的安全含义、`sub` 是字符串还是整数）但**没意识到自己应该问**。要靠 §5.3 的代码 diff 和 §5.4 的修订决定来检验它是不是只是"碰巧蒙对"。

### 5.2 Cursor 与原意不一致的解读


第一轮里 Cursor 的"我理解的目标 / 下一步 / 第一个失败测试名"复述与 SPEC + PLAN 完全一致：

- 目标复述准确——"仅依据 SPEC 和 PLAN" + "TDD 先写失败测试"。
- 下一步动作正确——创建 `tests/test_auth.py`。
- 第一个测试名 `test_password_hash_and_verify` 与 PLAN 步骤 1 的失败测试名一致。

这说明在**任务理解层面**没有偏离。但任务理解不偏离 ≠ 实现不偏离。最终是否有"超出 SPEC 范围"或"细节微偏"，需要等 §5.3 它产出的代码与主线对比之后再下结论。

### 5.3 它产出的代码 / 测试与预期的差距


实际产物（位于 `.worktrees/cold-start/backend/`）：

#### `app/auth/__init__.py`

空文件，与 SPEC/PLAN 一致。

#### `app/auth/password.py`（**与主线版本不同**）

```python
try:
    from passlib.context import CryptContext
except ModuleNotFoundError:
    CryptContext = None

if CryptContext is not None:
    _ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
else:
    _ctx = None


def hash_password(plain: str) -> str:
    if _ctx is None:
        raise ModuleNotFoundError("passlib is required for password hashing")
    return _ctx.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    if _ctx is None:
        raise ModuleNotFoundError("passlib is required for password hashing")
    return _ctx.verify(plain, hashed)
```

**与主线版本 diff**：

```diff
- from passlib.context import CryptContext
-
- _ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
-
-
- def hash_password(plain: str) -> str:
-     return _ctx.hash(plain)
+ try:
+     from passlib.context import CryptContext
+ except ModuleNotFoundError:
+     CryptContext = None
+
+ if CryptContext is not None:
+     _ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
+ else:
+     _ctx = None
+
+ def hash_password(plain: str) -> str:
+     if _ctx is None:
+         raise ModuleNotFoundError("passlib is required for password hashing")
+     return _ctx.hash(plain)
```

**意义**：Cursor 自作主张加了一段"passlib 没装也能 import 不报错"的软兜底。但 SPEC §4 与 PLAN 任务 1 已明确把 `passlib[bcrypt]==1.7.4` 列为硬依赖，且 PLAN 任务 2 步骤 1 的失败测试就期望"未装时直接 ModuleNotFoundError"。Cursor 这段兜底**违背了 fail-fast 原则**——在生产里它会让"没装 passlib"这种本应启动期暴露的错误，被推迟到第一次 `hash_password()` 才报，反而难排查。

#### `app/auth/jwt_utils.py`（**与主线一字不差**）

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

**意义**：Cursor 与主线一字不差，证明 SPEC §4 的"HS256 / 7 天 / `JWT_SECRET` fallback / `sub=str(user_id)`"四条边界写得**足够明确**——甚至连默认值字符串 `"dev-secret-change-me"` 都和我们一致。

#### `tests/test_auth.py`（**超出 PLAN 任务 2 范围**）

PLAN 任务 2 只要求 3 个失败测试：`test_password_hash_and_verify`、`test_jwt_round_trip`、`test_jwt_invalid`。Cursor 实际产出 **10 个**测试，把任务 1（users 表）、任务 3（注册/登录/me 路由）的测试一并写完：

| 测试名 | 属于 PLAN 哪个任务 |
|---|---|
| `test_users_table_exists` | 任务 1 |
| `test_password_hash_and_verify` | **任务 2（指定）** |
| `test_jwt_round_trip` | **任务 2（指定）** |
| `test_jwt_invalid_raises` | **任务 2（指定）** |
| `test_register_returns_token` | 任务 3 |
| `test_register_duplicate_username_409` | 任务 3 |
| `test_register_username_validation` | 任务 3 |
| `test_login_success_and_failure` | 任务 3 |
| `test_me_requires_token` | 任务 3 |
| `test_me_returns_current` | 任务 3 |

**意义**：Cursor 第一轮"复述目标"明明说了"完成任务 2"，但实际写测试时直接把后续任务的测试一起补上。这是 §5.2 里我提到的"任务理解层面没偏离 ≠ 实现不偏离"的实证。它没问、没声明、就自行扩了 scope。

### 5.4 修订前后的 SPEC / PLAN 关键 diff


#### Cursor 跑出的 pytest 输出（按时间顺序）

```
# 第一次（红）—— SPEC/PLAN 没有覆盖到的环境兼容性问题
ImportError: cannot import name 'field_validator' from 'pydantic'
ModuleNotFoundError: No module named 'passlib'
1 failed, 2 passed, 4 warnings, 7 errors in 2.25s

# 第二次（红）—— 修了部分兼容性后剩下的问题
TypeError: Client.__init__() got an unexpected keyword argument 'app'
PydanticUserError: root_validator ...
1 failed, 2 passed, 4 warnings, 7 errors in 2.00s

# 第三次（绿）
10 passed in 6.58s
```

#### 由冷启动反馈触发的 SPEC / PLAN 修订点

| 反馈点 | 由此对 SPEC/PLAN 的修订 |
|---|---|
| **F1 — Cursor 给 `passlib import` 加软兜底** | SPEC §4 应增加一行"硬依赖必须 fail-fast，不允许 try/except 软兜底"；PLAN 任务 2 步骤 3 的参考实现需要在最顶部一行注释 `# passlib 是硬依赖，禁止 try/except` |
| **F2 — Cursor 自行写出任务 1、任务 3 的测试** | PLAN 任务 2 步骤 1 应明确写"**只**写下面 3 个测试，不要补任务 1 / 任务 3 的测试"；并在 SPEC 的 §0 工作流约定里加一条"task 范围严格按 PLAN，不主动扩展" |
| **F3 — PLAN 任务 2 步骤 2 期望"3 个新增 fail"，实际 cold-start 环境先红在依赖兼容性** | PLAN 任务 1 步骤 4 的依赖安装命令里需要明确 `pydantic>=2`、`httpx>=0.27`、`fastapi>=0.115` 的最低版本；conftest 的 `TestClient(app=...)` 在新版 httpx 里要改 `TestClient(transport=ASGITransport(app=...))` 或确保 `httpx<0.28` |
| **F4 — Cursor 没问任何澄清问题就一次跑完** | 这本身证明 SPEC §3.1–§4 + PLAN 节选已足够明确——保留为正面证据。但 F1/F2 提示我们：**Cursor 不问 ≠ 它没踩坑**——它会"自己脑补默认行为"。SPEC 应明文加上"未明确的事请优先停下来问，而不是自行假设" |

#### 修订前后关键 diff（unified）

```diff
--- a/docs/superpowers/specs/2026-06-13-user-auth-and-my-posts.md
+++ b/docs/superpowers/specs/2026-06-13-user-auth-and-my-posts.md
@@ §4 非功能性需求
- - **安全**：bcrypt 哈希；JWT HS256，密钥从 `JWT_SECRET` 环境变量读取，缺失时使用本地默认值（仅开发用）；token 有效期 7 天；不实现 refresh。
+ - **安全**：bcrypt 哈希；JWT HS256，密钥从 `JWT_SECRET` 环境变量读取，缺失时使用本地默认值（仅开发用）；token 有效期 7 天；不实现 refresh。
+   - **依赖必须 fail-fast**：`passlib`、`PyJWT` 等硬依赖在导入失败时直接抛 `ImportError`，**不允许写 `try/except ModuleNotFoundError` 软兜底**。
+
+ ### §0 工作流约定（新增）
+ - 每个 task 的 scope 严格按 PLAN：只写 PLAN 明列的失败测试，不主动补充其他 task 的测试。
+ - SPEC 没明确的事，优先停下来问，**禁止"凭默认值脑补继续"**。
```

```diff
--- a/docs/superpowers/plans/2026-06-13-user-auth-and-my-posts-plan.md
+++ b/docs/superpowers/plans/2026-06-13-user-auth-and-my-posts-plan.md
@@ 任务 1 / 步骤 4 安装依赖
- pip install passlib[bcrypt]==1.7.4 bcrypt==4.0.1 PyJWT==2.8.0
+ pip install -r backend/requirements.txt   # 包含 fastapi>=0.115, pydantic>=2, httpx>=0.27
+ # 上述 requirements 文件已经把 passlib/bcrypt/PyJWT 写死版本
+ # 注意：httpx>=0.28 的 TestClient 不再接受 `app=...` 关键字，conftest 用 ASGITransport 包装
@@ 任务 2 / 步骤 1
- 写失败测试 tests/test_auth.py（3 个）
+ 写失败测试 tests/test_auth.py（**只写下列 3 个，不要补任务 1/任务 3 的测试**）
+   - test_password_hash_and_verify
+   - test_jwt_round_trip
+   - test_jwt_invalid_raises
@@ 任务 2 / 步骤 3
- 实现 password.py（参考骨架略）
+ 实现 password.py（**禁止 try/except ModuleNotFoundError 包装；passlib 是硬依赖**）
```

> 说明：以上 diff 仅反向说明"冷启动反馈对 SPEC/PLAN 应有的修订"，是对照证据。**主线代码已经按主开发版本实现**（不含软兜底、范围严格按 task），所以 main 分支无需重新落地这两处 diff，但下一次写新 SPEC 时应直接沿用这些约定。

---

## 6. 对 Superpowers `brainstorming` 技能的反思

### 做得好的地方

1. **"先问再写"的纪律**：每次它都先抛 1 个澄清问题，我答完它再继续，避免了"一上来就生成代码"。
2. **分块签字**：把 SPEC 拆成 §1/§2/.../§7 让我逐节确认，比"一份长文档审一遍"准确率高得多。
3. **隐私 / 边界敏感**：在我容易忽略的地方（列表 schema vs 详情 schema、`contact_type` 矩阵、`mine` 与 401）主动提醒。

### 不满的地方

1. **scope 倾向蔓延**：每一期它都倾向"顺手把…也做了"。需要我硬手收敛，特别是视觉重构那期。
2. **深度依赖隐性默认值**：写 SPEC 时它会偷偷塞"`JWT_SECRET` 缺失时回 fallback 默认值"这种带安全风险的默认；要靠人类 reviewer 抓出来。
3. **OD/MCP 等外部依赖**：建议时不看运行环境，一次性把"需要装 6 个东西"的方案丢出来。
4. **测试 fixture 改造的工作量评估偏低**：第 6 期 anon → user 的迁移，AI 估"少量改动"，实际把 60 个测试用例的 header 都改了。

---

## 7. 后续

冷启动 5.1–5.4 待跑完 Cursor 后回填。一旦回填，§5.4 的修订会反向改 SPEC 与 PLAN，并在此处给 unified diff 做闭环证据。
