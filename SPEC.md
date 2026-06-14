# SPEC.md — 南哪寻宝 / NJU LostFound 整体设计文档

> 状态：实现完成（覆盖发帖、列表筛选、详情交互、编辑/删除、视觉重构、用户系统六期）  
> 仓库：<https://github.com/Arrebol88/Lost_and_Found>  
> 本文档汇总性质：作为"对外交付的整体规约"。**详细规约保存在 `docs/superpowers/specs/*.md` 的 6 份分模块 SPEC 中**，本文档对其引用而不重复。

---

## 1. 问题陈述

南京大学是一所有 4 个校区、10 万 + 师生的大型综合性大学，每天都有大量物品被遗失或拾得。现状：

- **官方渠道空缺**：学校没有跨校区统一的失物招领平台。
- **现有方案碎片化**：QQ 群 / 朋友圈 / 论坛贴；信息易被淹没、跨校区无法触达、找回率低。
- **匿名诉求**：丢失贵重物品（电子产品 / 证件）的人不愿在公开社交平台暴露真实身份。

**目标用户**：

| 用户画像 | 痛点 |
|---|---|
| 丢东西的师生 | 不知该去哪找；不愿在朋友圈暴露身份；担心私人联系方式被广播 |
| 拾到东西的师生 | 不知如何高效找到失主；不愿留私人电话被骚扰 |
| 跨校区学生 | 鼓楼丢的东西可能被仙林校区的人捡到，跨校区匹配渠道缺失 |

**为什么值得做**：哪怕只缩短 30% 的"丢-认领"匹配时间，这个平台就有真实的留存价值。

**30 秒一句话**：

> 一个针对南京大学 4 个校区的失物招领平台。匿名发帖、按校区/物品种类/时间筛选、点赞与评论互动；账号体系让"我的帖子"可跨设备查询。

---

## 2. 用户故事（INVEST）

详见 6 份分模块 SPEC，本节列出贯穿全局的核心 5 条：

1. **作为丢东西的同学**，我可以发布一条"寻物"帖（标题 / 类别 / 校区 / 时间 / 描述 / 联系方式 / 选填图片），让全校师生看到。
2. **作为拾到东西的同学**，我可以发布一条"寻主"帖，并选择 自取 / 联系方式 / 已交管理处 三种交付方式。
3. **作为浏览者**，我可以在首页按物品种类、丢失/捡到时间、校区地点筛选；卡片快速预览，点进详情看完整字段。
4. **作为帖子作者**，我可以在详情页编辑/删除自己的帖子；其他用户只能点赞和评论，不能修改我的帖子。
5. **作为注册用户**，我可以用用户名 + 密码跨设备登录，"我的帖子" tab 跨浏览器访问自己发过的全部帖子。

---

## 3. 功能模块清单

每个模块都有自己的 SPEC 与 PLAN，本表是索引。

| # | 模块 | SPEC | PLAN |
|---|---|---|---|
| 1 | 发帖 | [post-creation-design](docs/superpowers/specs/2026-06-13-post-creation-design.md) | [post-creation-plan](docs/superpowers/plans/2026-06-13-post-creation-plan.md) |
| 2 | 列表 / 筛选 | [post-listing-filters-design](docs/superpowers/specs/2026-06-13-post-listing-filters-design.md) | [post-listing-filters-plan](docs/superpowers/plans/2026-06-13-post-listing-filters-plan.md) |
| 3 | 详情 / 点赞 / 评论 | [post-detail-interactions-design](docs/superpowers/specs/2026-06-13-post-detail-interactions-design.md) | [post-detail-interactions-plan](docs/superpowers/plans/2026-06-13-post-detail-interactions-plan.md) |
| 4 | 编辑 / 删除 | [post-edit-delete-design](docs/superpowers/specs/2026-06-13-post-edit-delete-design.md) | [post-edit-delete-plan](docs/superpowers/plans/2026-06-13-post-edit-delete-plan.md) |
| 5 | 视觉重构（Open Design 方法论） | [open-design-visual-refresh](docs/superpowers/specs/2026-06-13-open-design-visual-refresh.md) | [open-design-visual-refresh-plan](docs/superpowers/plans/2026-06-13-open-design-visual-refresh-plan.md) |
| 6 | 用户系统 / 我的帖子 | [user-auth-and-my-posts](docs/superpowers/specs/2026-06-13-user-auth-and-my-posts.md) | [user-auth-and-my-posts-plan](docs/superpowers/plans/2026-06-13-user-auth-and-my-posts-plan.md) |

---

## 4. 非功能性需求

- **性能**：单 SQLite，预期百级 QPS；列表 20–50 项查询毫秒级；详情页首屏 < 200ms。
- **安全**：bcrypt 密码哈希；JWT HS256（密钥环境变量注入，7 天过期、无 refresh）；图片 magic bytes 双校验防伪造；写操作必须登录。
- **可用性**：未登录可浏览首页与详情；写操作触发登录弹窗；中文 detail 错误文案。
- **可观测性**：FastAPI 自带 OpenAPI；后端 401/409/422 在 `detail` 字段返回中文文案，前端友好展示。
- **可移植性**：单条 `docker compose up --build` 即可全栈启动；CI 自动构建并推到 GHCR。

---

## 5. 系统架构

```
┌──────────────────────────────────────────────────────────────┐
│ Browser                                                       │
│  ┌──────────────────────────────────────────────┐             │
│  │ Vue 3 SFC (vite build)                       │             │
│  │  ├── App.vue / Hero / Tabs / AuthDialog      │             │
│  │  ├── PostList / PostCard / PostFilters       │             │
│  │  ├── PostDetail / CommentList / CommentForm  │             │
│  │  └── auth.js + api.js (axios + interceptor)  │             │
│  └──────────────────────────────────────────────┘             │
└────────────┬──────────────────────────────────────────────────┘
             │ HTTP(S) JSON / multipart  Authorization: Bearer
             ▼
┌──────────────────────────────────────────────────────────────┐
│ FastAPI (uvicorn, port 8000)                                  │
│  ├── routers/auth.py          (register / login / me)         │
│  ├── routers/posts.py         (CRUD + likes + listing)        │
│  ├── routers/comments.py      (CRUD on comments)              │
│  ├── auth/{password,jwt,deps} (bcrypt + PyJWT + DI 解析)      │
│  ├── schemas.py               (Pydantic v2)                   │
│  ├── models.py                (SQLAlchemy)                    │
│  ├── storage.py               (图片落盘 + magic bytes 校验)   │
│  └── database.py              (init_db + 旧 anon_id 清表)     │
└────────────┬──────────────────────────────────────────────────┘
             │
             ▼
   ┌─────────────────┐    ┌──────────────────┐
   │ SQLite          │    │ Local FS         │
   │ nju_lostfound.db│    │ uploads/         │
   └─────────────────┘    └──────────────────┘
```

---

## 6. 数据模型

```sql
CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username VARCHAR(32) NOT NULL UNIQUE COLLATE NOCASE,
  password_hash VARCHAR(128) NOT NULL,
  created_at DATETIME NOT NULL
);

CREATE TABLE posts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  post_type VARCHAR(16) NOT NULL CHECK (post_type IN ('found','lost')),
  title VARCHAR(50) NOT NULL,
  category VARCHAR(32) NOT NULL,        -- 9 类（详见模块 1）
  image_path TEXT,
  description TEXT,
  location VARCHAR(100) NOT NULL,       -- gulou / xianlin / suzhou / pukou
  event_time DATETIME NOT NULL,
  contact_type VARCHAR(32) NOT NULL,    -- self_pickup / contact / handed_over / owner_contact
  contact_detail VARCHAR(200) NOT NULL,
  created_at DATETIME NOT NULL,
  user_id INTEGER NOT NULL REFERENCES users(id)
);

CREATE TABLE post_likes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  post_id INTEGER NOT NULL REFERENCES posts(id),
  user_id INTEGER NOT NULL REFERENCES users(id),
  created_at DATETIME NOT NULL,
  UNIQUE (post_id, user_id)
);

CREATE TABLE post_comments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  post_id INTEGER NOT NULL REFERENCES posts(id),
  user_id INTEGER NOT NULL REFERENCES users(id),
  content VARCHAR(200) NOT NULL,
  image_path TEXT,
  created_at DATETIME NOT NULL
);
```

---

## 7. API 设计

| 方法 | 路径 | 鉴权 | 简述 |
|---|---|---|---|
| POST | `/api/auth/register` | 否 | 注册并返回 `{token, user}` |
| POST | `/api/auth/login` | 否 | 登录 |
| GET | `/api/auth/me` | 是 | 当前用户 |
| GET | `/api/posts` | 可选 | 列表；支持 `post_type` / `category` / `location` / `time_range` / `mine` |
| POST | `/api/posts` | 是 | 创建（multipart） |
| GET | `/api/posts/{id}` | 可选 | 详情；带 `mine` `liked_by_me` `like_count` |
| PUT | `/api/posts/{id}` | 是 | 仅作者，编辑（multipart） |
| DELETE | `/api/posts/{id}` | 是 | 仅作者，级联删除评论/点赞/图片 |
| POST | `/api/posts/{id}/likes` | 是 | toggle |
| GET | `/api/posts/{id}/comments` | 可选 | 评论列表 |
| POST | `/api/posts/{id}/comments` | 是 | 发评论 |
| DELETE | `/api/comments/{id}` | 是 | 仅评论作者 |

错误码：401 未登录 / 登录失效；403 不是作者；404 资源不存在；409 用户名占用；413 图片超限；422 字段校验失败。

完整字段与边界条件见各分模块 SPEC。

---

## 8. 技术选型与理由

| 层 | 选型 | 理由 |
|---|---|---|
| 后端框架 | FastAPI | Pydantic v2 + 自动 OpenAPI；DI 模式契合 `get_current_user` |
| ORM | SQLAlchemy 2.x | 与 FastAPI 主流栈匹配；声明式模型清晰 |
| 数据库 | SQLite | 单文件、零运维；本作业规模无需 PG |
| 哈希 | passlib[bcrypt] | 行业默认；与 Pydantic v2 兼容 |
| Token | PyJWT (HS256) | 无状态、无需 session 表 |
| 前端 | Vue 3 SFC + Vite | SFC 阅读体验好；Vite HMR 极快 |
| HTTP | axios | 拦截器机制贴合 token 自动注入与 401 自动登出 |
| 测试 | pytest（后端 74）+ Vitest（前端 48） | 主流；与 CI 兼容性好 |
| 容器 | Docker + docker-compose | 单条命令拉起全栈；CI 自动构建并推到 GHCR |

### 8.1 前端设计系统

> 题面要求"明确所选 Open Design 设计系统（71 选 1 或自定义）与适用 skill"。

- **设计系统**：自定义"Notion 暖灰" — 偏 `notion` 风格，但不直接复刻 LOGO；色板以 `#FAF9F7` 暖灰为底，紫色 `#6B5BD2` 为强调色。
- **适用 Open Design skill 类比**：列表页对应 `dashboard`-light、详情页对应 `blog`-reading 模板。
- **执行偏离**：本期未运行 Open Design CLI / MCP（环境约束），改为"离线借用方法论"——产物 [DESIGN.md](DESIGN.md) 等同于 Open Design 的 brand-spec；P0/P1/P2 自评清单与 5 维反 AI-slop 自查全程执行。详见 [AGENT_LOG.md](AGENT_LOG.md)。

---

## 9. 验收标准（汇总）

| 模块 | 完成判定 |
|---|---|
| 发帖 | 后端 `pytest backend/tests/test_posts_*` 全过；前端 PostForm 提交成功后跳回首页 |
| 列表 / 筛选 | `tests/test_posts_list` 全过；切 tabs / filter 网络面板能看到对应 query 参数 |
| 详情 / 交互 | `tests/test_post_detail.py + test_post_likes.py + test_post_comments.py` 全过 |
| 编辑 / 删除 | `tests/test_post_edit + test_post_delete` 全过；他人编辑/删除返回 403 |
| 视觉重构 | 列表 + 详情两条主线没有硬编码颜色（除 `tokens.css` 17 处定义）；P0/P1/P2 清单全勾 |
| 用户系统 | `tests/test_auth.py` 全过；前端可注册/登录/登出；"我的帖子" tab 切换后调 `mine=true` |
| 整体 | `npm run build` 成功；`docker compose up --build` 一键启动；CI 在 GitHub Actions 三 job 全绿 |

---

## 10. 风险与未决问题

| 风险 | 缓解 / 现状 |
|---|---|
| SQLite 并发写瓶颈 | 当前无；规模上来后切 PG |
| JWT 密钥泄露 | 必须通过环境变量 `JWT_SECRET` 注入；缺失时 fallback 仅限本地开发 |
| 图片伪造 | magic bytes 双校验；上传体积限制 5MB |
| 历史 anon_id 数据兼容 | 已在数据库 `init_db()` 中"检测到旧 schema 即清空"，破坏性升级，已在 README 警告 |
| Open Design CLI 未实跑 | 在 `AGENT_LOG.md` 与本文档 §8.1 已记录偏离 |
| 代码量贴近规模下限（~3000 行） | 后续可加状态流转 / 关键词搜索两期补到 3500+ |

---

## 11. 详细设计参考

| 主题 | 详情入口 |
|---|---|
| 6 期分模块 SPEC | [docs/superpowers/specs/](docs/superpowers/specs/) |
| 6 期分模块 PLAN | [docs/superpowers/plans/](docs/superpowers/plans/) |
| 品牌契约 | [DESIGN.md](DESIGN.md) |
| 智能体协作过程 | [SPEC_PROCESS.md](SPEC_PROCESS.md) |
| 实现日志 | [AGENT_LOG.md](AGENT_LOG.md) |
