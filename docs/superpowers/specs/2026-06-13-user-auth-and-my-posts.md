# 设计：用户注册 / 登录与 "我的帖子"

> 状态：已确认  
> 创建日期：2026-06-13  
> 范围：后端引入用户表 + JWT 鉴权；现有匿名 ID 体系全部替换；前端新增登录/注册入口与 "我的帖子" tab；旧数据清空。

## 1. 问题陈述

现有项目的所有写操作（发帖、点赞、评论、编辑、删除）依赖浏览器侧 `localStorage` 中持久化的随机 UUID（`X-Anon-Id`）作为身份标识。它带来三个问题：

1. **不可识别真实用户**：换浏览器即换身份，"我发的帖子"无法跨设备查询。
2. **无认证强度**：任何人都能伪造 header 操作他人帖子，编辑/删除虽有 anon_id 校验也仅是"安慰剂"。
3. **演示价值低**：作业要求至少 3–5 个核心模块，纯匿名身份让"用户系统"模块缺位。

本期改造把身份从"浏览器 UUID"切换为"用户名 + 密码 + JWT"，并新增首页 tab "我的帖子"。

## 2. 用户故事

1. 作为新访客，我可以用用户名 + 密码 30 秒内注册并自动登录。
2. 作为已注册用户，我可以在任何浏览器登录后访问自己的帖子。
3. 作为登录用户，我点击 tab "我的帖子" 即可看到自己发过的全部帖子。
4. 作为未登录访客，我能浏览首页与详情页，但点击"发帖 / 点赞 / 评论 / 编辑 / 删除"任一动作时被引导登录。
5. 作为帖子作者，详情页显示"作者：alice"，他人无法编辑或删除我的帖子。
6. 作为登录用户，我可以登出；登出后写操作回到要求登录态。

## 3. 功能规约

### 3.1 注册 `POST /api/auth/register`

- 入参：`{ username: str, password: str }`
- 校验：
  - `username`：3–32 个字符；允许字母、数字、下划线、汉字；用户名查重不区分大小写。
  - `password`：≥ 6 个字符；前后不去空格。
- 行为：成功写入 `users` 表（bcrypt 哈希），返回 token；失败返回 409（重名）/ 422（格式不合法）。
- 出参：`{ token: str, user: { id: int, username: str } }`，HTTP 201。

### 3.2 登录 `POST /api/auth/login`

- 入参：同上。
- 校验：用户存在 + bcrypt 密码匹配；任意一项不通过返回 401（统一文案 "用户名或密码错误"，不暴露用户存在性）。
- 出参：与注册一致；HTTP 200。

### 3.3 当前用户 `GET /api/auth/me`

- 必须登录；返回 `{ id, username }`，HTTP 200。
- 缺 token / token 非法 / 过期 → 401。

### 3.4 帖子接口

| 方法 | 路径 | 是否需登录 | 变更 |
|---|---|---|---|
| `POST` | `/api/posts` | 是 | 写入 `user_id`；不再有 `X-Anon-Id` |
| `GET`  | `/api/posts` | 否 | 新增可选 `mine=true`，未登录传 `mine=true` 返回 401 |
| `GET`  | `/api/posts/{id}` | 否 | 新增字段 `author_username`；`mine` 取决于登录态 |
| `PUT`  | `/api/posts/{id}` | 是 | 仅作者 |
| `DELETE` | `/api/posts/{id}` | 是 | 仅作者 |
| `POST` | `/api/posts/{id}/likes` | 是 | 切换；按 `user_id` 唯一 |
| `GET`  | `/api/posts/{id}/comments` | 否 | 新增 `author_username`、`mine` |
| `POST` | `/api/posts/{id}/comments` | 是 | 写入 `user_id` |
| `DELETE` | `/api/comments/{id}` | 是 | 仅评论作者 |

### 3.5 列表筛选 `mine`

- `mine=true` 时，列表只返回 `user_id == current_user.id` 的帖子。
- `mine=true` 与 `post_type` 互斥：当传 `mine=true` 时忽略 `post_type`，返回所有类型。
- 其他筛选（`category` / `time_range` / `location`）仍生效。

### 3.6 前端入口

- Hero 右侧：
  - 未登录：`登录` `注册` 两个按钮 → 弹 `AuthDialog`。
  - 登录后：用户名 chip + `登出`。
- Tabs：`寻物 / 寻主 / 我的帖子`，三选一。
- 切换到 `我的帖子`：
  - 未登录：渲染占位 `请先登录后查看你发布的帖子` + 登录按钮，不发请求。
  - 已登录：调用 `listPosts({ mine: true, ...filters })`，无 PostFilters 隐藏 `post_type` 选项；若返回为空，显示 `你还没有发布过帖子`。
- 写操作（发帖 / 点赞 / 评论 / 编辑 / 删除）：未登录时拦截并弹 `AuthDialog`；登录成功后**不**自动重试，由用户再次点击触发（避免误操作复杂状态机）。

### 3.7 评论显示

- 评论项额外显示作者用户名（小灰字 meta，紧邻时间）。
- 自己的评论 hover 时仍可见删除按钮。

## 4. 非功能性需求

- **安全**：bcrypt 哈希；JWT HS256，密钥从 `JWT_SECRET` 环境变量读取，缺失时使用本地默认值（仅开发用）；token 有效期 7 天；不实现 refresh。
- **性能**：列表查询保持原有索引；无新增 N+1（用户名直接 join）。
- **可观测性**：401/409 在响应体的 `detail` 字段返回中文文案，便于前端展示。
- **可访问性**：登录对话框焦点初始落在用户名输入框，回车提交。

## 5. 系统架构

```
backend/app/
├── auth/                     ← 新增
│   ├── jwt_utils.py          ← 编 / 解 token
│   ├── password.py           ← bcrypt 包装
│   └── deps.py               ← get_current_user / get_current_user_optional
├── models.py                 ← 新增 User 模型；改 anon_id → user_id
├── schemas.py                ← 新增 UserOut / RegisterIn / LoginIn / TokenOut；改 PostOut/CommentOut
├── database.py               ← init_db 检测旧 anon_id 列时清空表 + 文件
├── routers/
│   ├── auth.py               ← 新增 /auth/register, /login, /me
│   ├── posts.py              ← 切换依赖到 get_current_user(_optional)
│   └── comments.py           ← 同上
├── main.py                   ← 注册 auth 路由

frontend/src/
├── auth.js                   ← 新增 token & user 管理
├── api.js                    ← axios 拦截器附 Authorization；移除 ensureAnonId
├── components/
│   ├── AuthDialog.vue        ← 新增登录/注册模态框
│   ├── PostFilters.vue       ← 不变
│   └── ...                   ← 各组件不再读 X-Anon-Id
├── App.vue                   ← Hero 用户区 + 我的帖子 tab
```

## 6. 数据模型

```sql
CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username VARCHAR(32) NOT NULL UNIQUE COLLATE NOCASE,
  password_hash VARCHAR(128) NOT NULL,
  created_at DATETIME NOT NULL
);

ALTER TABLE posts          DROP COLUMN anon_id; ADD COLUMN user_id INTEGER NOT NULL REFERENCES users(id);
ALTER TABLE post_likes     DROP COLUMN anon_id; ADD COLUMN user_id INTEGER NOT NULL REFERENCES users(id);
ALTER TABLE post_comments  DROP COLUMN anon_id; ADD COLUMN user_id INTEGER NOT NULL REFERENCES users(id);

CREATE UNIQUE INDEX uq_post_likes_post_user ON post_likes(post_id, user_id);
```

迁移策略：启动时若发现 `posts` 仍有 `anon_id` 列且 `users` 表不存在，**清空** `posts / post_likes / post_comments` 三表；同时清空 `uploads/` 下所有文件；再 `Base.metadata.create_all`。该清空是一次性的，写入日志告警。

## 7. API 设计细节

### 7.1 鉴权 Header

- 请求：`Authorization: Bearer <jwt>`。
- 响应错误码：
  - `401 detail="未登录"` — 缺 token。
  - `401 detail="登录已失效，请重新登录"` — token 过期 / 解码失败 / 用户已不存在。
  - `403 detail="not your post"` — 操作他人资源（编辑、删除帖子或评论）。
  - `409 detail="用户名已被占用"` — 注册重名。
  - `422 detail="..."` — 输入格式不合法。

### 7.2 JWT 载荷

```json
{
  "sub": "<user_id:int>",
  "username": "<str>",
  "iat": 1736000000,
  "exp": 1736604800
}
```

后端解码后用 `sub` 反查 `users` 表确认用户仍存在。

## 8. 技术选型与理由

- `passlib[bcrypt]` —— Python 业界默认，自带 salt，与 SQLAlchemy 解耦。
- `PyJWT` —— 仅需 HS256 编解码，避免引入 fastapi-users / authlib 等重型依赖。
- 不引入 cookie / session：保持后端无状态，与项目整体风格一致。
- 前端不引入 vue-router / pinia：现有 view 状态机简单，沿用 `view = ref('home')` 即可。

## 9. 验收标准

P0（阻塞合并）：

- 注册 / 登录 / `/me` 三接口均有 happy path + 至少一个失败路径测试。
- 所有原本的 60 个后端测试要么改造为 "先注册后调用"，要么删除（被新功能替代），最终后端测试数 ≥ 60 全绿。
- 前端 38 个 vitest 用例 + 新增 ≥ 8 个鉴权 / 我的帖子用例全绿。
- `npm run build` 通过；`docker compose build` 通过（如 Docker Desktop 可用）。

P1：

- 未登录访问写操作必弹出 `AuthDialog`。
- "我的帖子" tab 行为符合 §3.6。
- 评论项显示 `author_username`。

P2：

- 登出后立即生效；token 过期被拦截器统一处理。
- AuthDialog 错误文案区分 "用户名已被占用" 与 "用户名或密码错误"。

## 10. 风险与未决问题

- **数据清空风险**：用户当前 DB 里只有少量测试数据，且作业要求 ≥ 3 模块，需要在 README 与 AGENT_LOG 中明确告知"启动一次会清空旧帖子"。
- **测试改造体量**：60 个用例都要套 `auth_headers` helper；若改造时有死锁，可在 conftest 暴露 `register_and_token()` fixture。
- **JWT_SECRET 默认值**：dev 默认值会出现在 git 历史；README 说明 "生产请覆盖"。
- **passlib bcrypt 版本兼容**：在 docker 镜像里需要 `pip install bcrypt`；当前 backend `requirements.txt` 没有。
