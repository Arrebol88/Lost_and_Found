# 帖子编辑与删除 — 设计规约

> 日期：2026-06-13
> 范围：在“南哪寻宝”已有发帖、列表、详情、点赞与评论功能基础上，给作者本人提供帖子编辑与删除入口。
> 不在此范围：登录系统、软删除、编辑历史/版本回滚、多图、`post_type` 修改。

---

## 1. 问题陈述

帖子发布后，作者可能因为信息错误、物品已找回等原因需要修改或撤下帖子。当前系统没有任何方式让作者更正或撤回自己发的帖子，只能由失主和拾物者继续在评论里答疑。本期补上：

1. 详情页右上角“编辑”按钮：进入编辑态，原帖内容预填，作者可改除 `post_type` 外的所有字段；
2. 详情页右上角“删除”按钮：二次确认后将帖子及其评论、点赞、相关图片一并清理；
3. 仅原作者（同一匿名 ID）可见上述按钮；后端额外做权限校验，避免越权。

目标用户依然是南京大学失主与拾物者；编辑/删除是“责任型”动作的最低必要保障。

---

## 2. 用户故事

1. 作为失主，我发现帖子里写错了校区，能在详情页点“编辑”，把校区改成正确值并保存，详情页立即反映新内容。
2. 作为拾物者，我把物品移交校警了，进入自己发的帖子点“删除”，二次确认后帖子及评论一并消失，回到首页不再出现。
3. 作为浏览者，我点开别人发的帖子，看不到“编辑/删除”按钮；即便我手动构造请求，后端也会以 403 拒绝。
4. 作为编辑中的作者，如果我中途反悔，能点“取消”退出编辑态；只有当我已经改过内容时，才提示二次确认。
5. 作为编辑中的作者，我能替换帖子首图，也能勾选“移除图片”把帖子改回无图。

---

## 3. 功能规约

### 3.1 详情页右上角入口

- 仅当响应中 `mine == true` 时渲染按钮区，否则按钮区不渲染。
- 按钮区包含两个按钮：`编辑`（次要按钮风格）、`删除`（红色危险按钮风格）。
- 点击“编辑” → 详情页内部 `mode` 切换为 `edit`，表单内容用当前帖子数据预填。
- 点击“删除” → 浏览器原生 `confirm('确认删除该帖子？此操作不可恢复')` → 通过则调用 DELETE → 成功后 emit `back`，App 回首页并刷新列表。

### 3.2 编辑态

- 表单字段（与发帖一致，但 **不含** `post_type`）：`title / category / description / location / event_time / contact_type / contact_detail`，加上图片输入控件。
- 图片处理：
  - 当前帖子有图：缩略图 + “移除当前图片”勾选框（`remove_image`）+ 重新上传输入。
  - 当前帖子无图：仅显示重新上传输入。
  - 若同时勾选移除并上传新图，则以新上传为准；移除勾选取消、未上传新图，则保留原图。
- 校验复用发帖逻辑（`PostCreate` 的 Pydantic 校验 + `storage.save_image`）。
- “保存”按钮位于帖子主体下方；提交时禁用，成功后切回 `mode=view` 并以返回值刷新 `post`。
- “取消”按钮位于编辑态右上角，靠近保存对侧；若未做修改直接退出，否则 `confirm('放弃未保存的修改？')` 通过后退出。

### 3.3 后端权限模型

- `posts` 表新增列 `anon_id TEXT(36)`，可空（兼容历史数据）。
- 创建帖子接口 `POST /api/posts` 依赖 `get_anon_id`，把作者匿名 ID 写入 `anon_id`。
- `GET /api/posts/{id}` 在 `PostDetailOut` 中新增 `mine: bool`，由当前请求 `anon_id` 与 `post.anon_id` 比较得出。
- `PUT /api/posts/{id}` 与 `DELETE /api/posts/{id}` 强制要求 `X-Anon-Id`，作者不匹配返回 403；帖子不存在返回 404；`post.anon_id IS NULL`（历史数据）一律视为非作者，403。
- 列表 `PostListItem`、详情 `PostDetailOut` 接口都不返回 `anon_id`，避免泄露身份。

### 3.4 删除联动

- DELETE 时按以下顺序清理：
  1. `post_comments` 下相关评论的图片文件 → `storage.delete_image`；
  2. 删 `post_comments` 行；
  3. 删 `post_likes` 行；
  4. 删 `posts` 主图文件（若存在）；
  5. 删 `posts` 行。
- 整个删除在单个 SQLAlchemy session 提交内完成；任一步骤异常 → rollback，未完成的图片删除以日志告警，不阻塞调用。

---

## 4. 非功能性需求

- **性能**：编辑保存与删除单接口在 200 ms 内返回（开发机本地）；图片清理顺序避免“DB 删除前文件已删除”导致的不一致。
- **安全**：所有写入接口必须经过 `get_anon_id`；越权请求统一返回 403，不区分“帖子不存在”和“非作者”可在文档与测试中明确区分。
- **健壮性**：图片落盘失败不应导致 DB 留下脏数据；DB 写失败时清理新落盘的图片。
- **可观测**：图片清理失败仅写 stderr 日志，不影响接口返回。

---

## 5. 系统架构

- **前端**：在 `PostDetail.vue` 内部维护 `mode` 状态；新增 `PostEdit.vue` 子组件，仅在 `mode==='edit'` 渲染；新增 `api.js` 的 `updatePost / deletePost`。`App.vue` 仍只在 home/picker/form/detail 之间切换；编辑态不引入新视图。
- **后端**：新增 `PUT /api/posts/{id}` 与 `DELETE /api/posts/{id}` 路由；`PostOut`/`PostDetailOut` 增加 `mine`；新增字段 `anon_id` 仅在 `models.Post` 与 `PostCreate` 内部流转。

---

## 6. 数据模型

`posts` 表新增列：

| 列 | 类型 | 约束 |
|---|---|---|
| anon_id | TEXT(36) | NULLABLE（兼容旧数据） |

无新增表。SQLite 不需要数据迁移脚本（仅追加列），通过 `Base.metadata.create_all` 在测试隔离 DB 中创建；线上 DB 通过启动前一次性 `ALTER TABLE` 加列。后端代码中通过 `_ensure_column` 工具在 `init_db()` 中检测列是否存在，缺则 `ALTER`。

---

## 7. API 设计

### 7.1 `POST /api/posts`（变更）

- 仍是 multipart；新增依赖 `get_anon_id`，把 `X-Anon-Id` 写入 `posts.anon_id`。
- 缺少或非法的 `X-Anon-Id` 返回 400（行为与点赞/评论一致）。
- 返回结构不变。

### 7.2 `GET /api/posts/{id}`（变更）

- 响应增加字段 `mine: bool`。

### 7.3 `PUT /api/posts/{id}`（新增）

- header：`X-Anon-Id` 必填。
- 表单字段：`title / category / description / location / event_time / contact_type / contact_detail`（必填规则与发帖一致）。
- 可选 `image`（multipart 文件）与 `remove_image`（form 字符串 `"true"`/`"1"` 视为真）。
- 行为：
  1. 帖子不存在 → 404。
  2. `post.anon_id != X-Anon-Id` → 403。
  3. 复用 `PostCreate` 校验载荷（不含 `post_type`，沿用旧 `post.post_type` 用于 `_contact_match_post_type` 校验）。
  4. 图片：若上传 `image`，落盘并准备替换；否则若 `remove_image=true`，准备清空；否则保留旧路径。
  5. DB 更新成功后再删除被替换/被移除的旧图。
- 返回：`PostDetailOut`（含 `like_count / liked_by_me / mine`）。

### 7.4 `DELETE /api/posts/{id}`（新增）

- header：`X-Anon-Id` 必填。
- 行为同 §3.4。
- 返回 204。
- 错误：`404 post not found`、`403 not your post`、`400 anon_id`。

---

## 8. 技术选型与理由

- 维持既有技术栈（FastAPI + SQLAlchemy + SQLite + Vue 3 + Vite + axios），不引入额外依赖。
- 不引入路由库：编辑态在 `PostDetail.vue` 内部用 `mode` 状态切换，避免在 SPA 中再插入第四个视图分支。
- 不引入软删除：作业范围内不需要恢复机制；级联删除更直接。
- 不引入登录：复用既有 `X-Anon-Id` 弱身份方案，与发帖、点赞、评论保持同一思路。

---

## 9. 验收标准

1. 同一浏览器发的帖子，详情页能看到“编辑/删除”按钮；换浏览器看同一帖看不到。
2. 点编辑 → 表单预填当前帖内容；保存成功后详情页字段更新，按钮区仍可见。
3. 编辑时未做修改 → 取消直接退出；做过修改 → 取消会先弹二次确认。
4. 编辑时勾选“移除图片”并保存：返回数据 `image_path` 为 `null`，原文件被删。
5. 编辑时上传新图：原图被删，DB 与磁盘以新图为准。
6. 越权 PUT/DELETE 返回 403。
7. DELETE 成功后：列表接口不再包含该帖；该帖评论、点赞、所有相关图片在磁盘上不存在；前端跳回首页并刷新。
8. 后端 pytest 全绿；前端 Vitest 全绿；`docker compose build` 成功。

---

## 10. 风险与未决问题

- **匿名 ID 仍易伪造**：与既有方案同等水平；REFLECTION 中将再次声明。
- **历史脏数据无作者**：旧帖子 `anon_id IS NULL`，所有人都不能改/删；可接受。
- **`ALTER TABLE` 启动期需求**：线上容器 DB 已有数据，不能简单 drop/recreate；以一次性 `ALTER TABLE posts ADD COLUMN anon_id TEXT` 解决。
- **图片清理与 DB 一致性**：先 commit DB 再删图；删图失败仅日志，避免 DB 状态与文件持续不一致带来的二次故障。
