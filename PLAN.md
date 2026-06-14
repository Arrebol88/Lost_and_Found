# PLAN.md — 实现计划总览

> 本文件汇总 6 期分模块计划（每期均由 `writing-plans` 技能产出 + 严格 TDD 红→绿执行 + worktree 隔离 + 完成后合并到 main）。  
> 每期的详细任务表保存在 `docs/superpowers/plans/*.md`，本文件只列出"执行轨迹"，作为对外交付的整体 PLAN。

仓库：<https://github.com/Arrebol88/Lost_and_Found>

---

## 0. 执行原则

每期均按以下流程：

1. **Brainstorming** → 主开发 agent 用 `superpowers:brainstorming` 分块呈现设计，用户逐节签字 → 沉淀 SPEC。
2. **writing-plans** → 把 SPEC 拆成 8–11 个 2–5 分钟级 task；每个 task 注明：目标、涉及文件、实现要点、**先写哪条失败测试**、跑哪条命令验证绿。
3. **using-git-worktrees** → 为每期开一个 `.worktrees/<feature>` worktree、对应分支 `feature/<feature>`。
4. **subagent-driven-development**（在 Trae 中无真子代理，按主会话内联 + 任务间自审，详见 [AGENT_LOG.md](AGENT_LOG.md)）→ 每个 task 严格 TDD：
   - 写失败测试
   - 跑测试看红
   - 写最少代码使其绿
   - 重构（按需）
5. **finishing-a-development-branch** → 全套测试 + build 通过后 `--no-ff merge` 回 main，删 worktree + 分支。

---

## 1. 6 期执行轨迹

### 第 1 期：发帖

- **SPEC**：[post-creation-design](docs/superpowers/specs/2026-06-13-post-creation-design.md)
- **PLAN**：[post-creation-plan](docs/superpowers/plans/2026-06-13-post-creation-plan.md)
- **任务数**：~10
- **关键文件**：`backend/app/{models,schemas,storage,routers/posts}.py`、`frontend/src/components/{TypePicker,PostForm}.vue`
- **测试**：`backend/tests/test_posts_*.py`（创建路径覆盖文本字段、location 枚举、contact_type 矩阵、图片 magic bytes、5MB 上限、字段长度边界）+ 前端 PostForm.test.js
- **完成判定**：后端 + 前端测试全绿，后端可通过 multipart 接收图片并落到 `uploads/`

### 第 2 期：列表 / 筛选

- **SPEC**：[post-listing-filters-design](docs/superpowers/specs/2026-06-13-post-listing-filters-design.md)
- **PLAN**：[post-listing-filters-plan](docs/superpowers/plans/2026-06-13-post-listing-filters-plan.md)
- **关键文件**：`backend/app/routers/posts.py::list_posts`、`frontend/src/components/{PostList,PostCard,PostFilters,App}.vue`
- **测试**：列表筛选交叉用例（post_type × category × location × time_range），列表 schema 与详情 schema 字段隔离

### 第 3 期：详情 / 点赞 / 评论

- **SPEC**：[post-detail-interactions-design](docs/superpowers/specs/2026-06-13-post-detail-interactions-design.md)
- **PLAN**：[post-detail-interactions-plan](docs/superpowers/plans/2026-06-13-post-detail-interactions-plan.md)
- **关键文件**：`backend/app/routers/{posts,comments}.py`、`PostDetail.vue` `CommentForm.vue` `CommentList.vue`
- **测试**：点赞 toggle 同一用户、跨用户独立计数；评论排序（created_at desc）；评论删除仅作者

### 第 4 期：编辑 / 删除

- **SPEC**：[post-edit-delete-design](docs/superpowers/specs/2026-06-13-post-edit-delete-design.md)
- **PLAN**：[post-edit-delete-plan](docs/superpowers/plans/2026-06-13-post-edit-delete-plan.md)
- **关键文件**：PUT/DELETE 路由 + `PostEdit.vue`
- **测试**：他人编辑 403、删除级联（评论 / 点赞 / 主图 / 评论图片）、图片替换/移除

### 第 5 期：视觉重构（Open Design 方法论）

- **SPEC**：[open-design-visual-refresh](docs/superpowers/specs/2026-06-13-open-design-visual-refresh.md)
- **PLAN**：[open-design-visual-refresh-plan](docs/superpowers/plans/2026-06-13-open-design-visual-refresh-plan.md)
- **任务数**：10
- **关键文件**：[DESIGN.md](DESIGN.md) + `frontend/src/styles/tokens.css` + 重排所有现有组件 scoped 样式
- **偏离声明**：未运行 Open Design CLI/MCP，改为"离线借用方法论"——按其 brand-spec 写 DESIGN.md、按其 5 维 + P0/P1/P2 清单自评。详见 [AGENT_LOG.md](AGENT_LOG.md)

### 第 6 期：用户系统 / 我的帖子

- **SPEC**：[user-auth-and-my-posts](docs/superpowers/specs/2026-06-13-user-auth-and-my-posts.md)
- **PLAN**：[user-auth-and-my-posts-plan](docs/superpowers/plans/2026-06-13-user-auth-and-my-posts-plan.md)
- **任务数**：11
- **关键文件**：
  - 后端新增：`auth/{__init__,password,jwt_utils,deps}.py`、`routers/auth.py`、`tests/test_auth.py`
  - 后端改造：`models.py` 引入 `users` 表 + `posts/post_likes/post_comments` 的 `anon_id → user_id`；`database.py` 启动检测旧 schema 时清空
  - 前端新增：`auth.js`、`AuthDialog.vue`、`tests/auth.test.js + AuthDialog.test.js`
  - 前端改造：`api.js` 删 `ensureAnonId` + 加 axios 拦截器；`App.vue` Hero 用户区 + "我的帖子" tab + 写操作登录拦截
- **破坏性升级**：在 `init_db()` 检测到旧 `posts.anon_id` 列时 DROP 三张表 + 清 uploads；README 已警告

---

## 2. 完成情况

| 模块 | 主线 commit | 状态 |
|---|---|---|
| 发帖 | merged to main | ✅ |
| 列表 / 筛选 | merged | ✅ |
| 详情 / 点赞 / 评论 | merged | ✅ |
| 编辑 / 删除 | merged | ✅ |
| 视觉重构 | merged（`feature/visual-refresh` → `84ac372`） | ✅ |
| 用户系统 | merged（`feature/user-auth` → `776b595`） | ✅ |

测试矩阵（最终）：

| 套件 | 用例数 | 状态 |
|---|---|---|
| backend `pytest -v` | 74 | passed |
| frontend `vitest --run` | 48 | passed |
| `npm run build` | — | OK |

---

## 3. 冷启动验证（§4.5）

详见 [SPEC_PROCESS.md §5](SPEC_PROCESS.md#5-冷启动验证-§45)。

- 验证 agent：Cursor（与主开发 Claude 类型不同）
- 选定 task：用户系统 PLAN 的任务 2「密码与 JWT 工具」
- 执行包：[`docs/superpowers/cold-start/cold-start-package.md`](docs/superpowers/cold-start/cold-start-package.md)
- worktree：`.worktrees/cold-start`，分支 `cold-start/cursor-t2`
- 状态：执行包已就绪，待跑

---

## 4. 详细任务表

| 期 | PLAN 详细文件 |
|---|---|
| 1. 发帖 | [post-creation-plan](docs/superpowers/plans/2026-06-13-post-creation-plan.md) |
| 2. 列表 / 筛选 | [post-listing-filters-plan](docs/superpowers/plans/2026-06-13-post-listing-filters-plan.md) |
| 3. 详情 / 点赞 / 评论 | [post-detail-interactions-plan](docs/superpowers/plans/2026-06-13-post-detail-interactions-plan.md) |
| 4. 编辑 / 删除 | [post-edit-delete-plan](docs/superpowers/plans/2026-06-13-post-edit-delete-plan.md) |
| 5. 视觉重构 | [open-design-visual-refresh-plan](docs/superpowers/plans/2026-06-13-open-design-visual-refresh-plan.md) |
| 6. 用户系统 | [user-auth-and-my-posts-plan](docs/superpowers/plans/2026-06-13-user-auth-and-my-posts-plan.md) |
