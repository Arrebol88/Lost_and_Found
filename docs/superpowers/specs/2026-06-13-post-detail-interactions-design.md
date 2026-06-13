# 帖子详情页与点赞、评论交互 — 设计规约

> 日期：2026-06-13  
> 范围：在“南哪寻宝”已有发帖与列表功能之上，增加帖子详情页、点赞与评论功能。  
> 不在此范围：登录系统、评论编辑、评论分页、点赞排行、通知系统。

---

## 1. 问题陈述

当前网站只有发帖与列表筛选，用户无法查看帖子详情，也无法对帖子进行任何互动。本次扩展引入：

1. 点击列表中的帖子卡片，进入帖子详情页；
2. 在详情页查看帖子全部信息（联系方式默认隐藏，需点击展开）；
3. 在详情页对帖子进行点赞 / 取消点赞；
4. 在详情页对帖子发表评论（文字必填、图片选填），并删除自己发表的评论。

目标用户依然是南京大学失主与拾物者；详情页是失主联系拾物者、双方留言确认线索的关键场景。

---

## 2. 用户故事

1. 作为失主，我点击列表中的“黑色雨伞”卡片，能在详情页看到完整描述与图片，从而判断是否是我的物品。
2. 作为浏览者，我在详情页可以点击点赞按钮表达关注，再点一次又能取消。
3. 作为拾物者的同学，我可以在评论里补充“今天下午我在 B 楼一楼也见过类似物品”，并可附上一张实物照片。
4. 作为评论作者，我打错字了，可以删除自己发表的评论；他人评论我看不到删除按钮。
5. 作为失主，我希望联系方式不要直接暴露在帖子卡片或详情页打开瞬间，而是点击“查看联系方式”后再展示，避免被无关方扫到。

---

## 3. 功能规约

### 3.1 帖子详情页

- **入口**：列表页 `PostCard.vue` 整张卡片可点击，点击后切换到详情视图。
- **展示字段**：标题、寻物/寻主类型、物品种类、校区、丢失/捡到时间、描述、首图、创建时间、联系方式类型、点赞数、`liked_by_me`、评论列表。
- **联系方式 contact_detail 默认隐藏**：详情页显示一个“查看联系方式”按钮；点击后才展开 `contact_detail`。
- **错误处理**：帖子不存在 → 详情页展示“帖子不存在或已被删除”，并提供返回首页按钮。

### 3.2 点赞

- **按钮位置**：详情页帖子主体下方，按钮文案随状态切换（未点赞=“点赞”，已点赞=“已点赞”），右侧紧跟点赞数。
- **行为**：每次点击切换状态。同一 `anon_id` + 同一 `post_id` 在数据库中要么存在一行（已点赞）要么不存在（未点赞）。
- **接口语义**：`POST /api/posts/{id}/likes`，使用 toggle 语义。返回 `{ liked: bool, like_count: int }`。
- **并发**：使用唯一约束 `(post_id, anon_id)`；并发情况下重复插入捕获并视为已点赞，重复删除视为未点赞，最终状态以 DB 为准。

### 3.3 评论

- **输入区**：文字 `<textarea>`（≤200 字符，必填，trim 后非空）；可选图片输入（jpg/png/webp，≤5MB），与发帖共用同一图片校验逻辑。
- **提交按钮**：仅在文字非空时可用。
- **列表**：详情页评论列表按 `created_at DESC` 时间倒序。
- **删除按钮**：仅当 `mine == true` 显示，点击后弹原生 `confirm` 二次确认后调用删除接口。
- **越权保护**：后端 `DELETE /api/comments/{id}` 校验 `X-Anon-Id == comment.anon_id`，否则 `403`。
- **图片处理**：评论删除时若有图片，连带删除磁盘上的文件，避免孤儿图片。

### 3.4 匿名身份

- 前端首次进入站点时若 `localStorage.nju_anon_id` 不存在，则生成 UUID v4 写入；后续所有请求统一通过 axios 拦截器附加 `X-Anon-Id`。
- 后端不持久化 `anon_id` 到独立用户表；它只作为点赞唯一键与评论作者标识。

---

## 4. 非功能性需求

- **性能**：单帖详情页接口、评论列表接口需在 200 ms 内返回（开发机本地）。
- **安全**：评论 / 点赞接口必须出现 `anon_id`；接口对 `X-Anon-Id` 做长度（36）与字符（UUID 形式）的格式校验，非法直接 `400`。
- **健壮性**：上传失败的评论不入库；DB 写入失败时清理已落盘的图片，避免孤儿文件。
- **隐私**：列表接口仍然不返回 `description`、`contact_detail`、`contact_type`；详情接口才返回 `contact_detail`。

---

## 5. 系统架构

- **前端**：在现有 Vue 3 SPA 上新增视图态 `view = 'detail'`，并新增 `PostDetail.vue / CommentForm.vue / CommentList.vue` 组件；`api.js` 扩展接口与匿名 ID 注入；`PostCard.vue` 增加点击 emit。
- **后端**：在现有 FastAPI 应用上新增 `routers/comments.py` 与扩展 `routers/posts.py`；models 新增 `PostLike`、`PostComment`；schemas 新增对应 Pydantic 模型；`storage.py` 复用，不再新增模块。

---

## 6. 数据模型

新增两张表，外键 `post_id → posts.id ON DELETE CASCADE`（SQLite 行为：业务层确保级联即可，无需启用 `PRAGMA foreign_keys`）。

### 6.1 `post_likes`

| 字段 | 类型 | 约束 |
|------|------|------|
| id | INTEGER | PK, AUTOINCREMENT |
| post_id | INTEGER | NOT NULL, FK → posts.id |
| anon_id | TEXT(36) | NOT NULL |
| created_at | DATETIME | NOT NULL |

唯一约束：`uq_post_likes_post_anon (post_id, anon_id)`。

### 6.2 `post_comments`

| 字段 | 类型 | 约束 |
|------|------|------|
| id | INTEGER | PK, AUTOINCREMENT |
| post_id | INTEGER | NOT NULL, FK → posts.id |
| anon_id | TEXT(36) | NOT NULL |
| content | TEXT | NOT NULL, CHECK length(content) BETWEEN 1 AND 200 |
| image_path | TEXT | NULLABLE |
| created_at | DATETIME | NOT NULL |

索引：`ix_post_comments_post_created (post_id, created_at DESC)`。

---

## 7. API 设计

所有需要 `anon_id` 的接口都通过 header `X-Anon-Id` 传递；缺失或非 UUID v4 字面量返回 `400 anon_id: 必须是 UUID`。

### 7.1 `GET /api/posts/{id}`

返回（200）：

```json
{
  "id": 1,
  "post_type": "lost",
  "title": "黑色雨伞",
  "category": "daily",
  "image_path": "uploads/2026/06/13/xxx.png",
  "description": "...",
  "location": "gulou",
  "event_time": "2026-06-12T18:30:00",
  "contact_type": "owner_contact",
  "contact_detail": "微信 abc123",
  "created_at": "2026-06-13T10:00:00",
  "like_count": 3,
  "liked_by_me": true
}
```

错误：`404 post not found`。

### 7.2 `POST /api/posts/{id}/likes`

- header：`X-Anon-Id` 必填。
- 行为：toggle。
- 返回：`{ "liked": true, "like_count": 4 }`。
- 错误：`404 post not found`、`400 anon_id`。

### 7.3 `GET /api/posts/{id}/comments`

- header：`X-Anon-Id` 必填（用于计算 `mine`）。
- 返回（200）：

```json
[
  {
    "id": 12,
    "post_id": 1,
    "content": "今天在 B 楼也见过",
    "image_path": null,
    "created_at": "2026-06-13T10:30:00",
    "mine": true
  }
]
```

### 7.4 `POST /api/posts/{id}/comments`

- header：`X-Anon-Id` 必填。
- 表单：`content`（必填），`image`（可选 multipart）。
- 返回 201：单条评论 JSON（结构同 7.3 单项）。
- 错误：`400 content`、`400 image`、`413 image too large`、`404 post not found`。

### 7.5 `DELETE /api/comments/{id}`

- header：`X-Anon-Id` 必填，必须等于 `comment.anon_id`。
- 行为：物理删除评论 + 关联图片文件。
- 返回 204。
- 错误：`404 comment not found`、`403 not your comment`。

---

## 8. 技术选型与理由

- 维持既有技术栈（FastAPI + SQLAlchemy + SQLite + Vue 3 + Vite + axios），不引入新依赖。
- 不引入路由库（vue-router）：既有应用是 `view` 三态切换，新增一态成本最低；`PostDetail.vue` 通过 props 接收 `postId`。
- 不引入登录：作业范围内匿名 ID 即可识别“同一访客”用于点赞与评论作者，避免引入 cookie/session/JWT 等额外复杂度。

---

## 9. 验收标准

1. 列表页点击任一卡片可进入详情页。
2. 详情页默认不显示 `contact_detail`，点击“查看联系方式”后才显示。
3. 同一浏览器对同一帖子点击点赞按钮：第 1 次点赞数 +1 且按钮状态变“已点赞”，第 2 次还原 -1，第 3 次再 +1。
4. 不同浏览器（不同 anon_id）对同一帖子点赞各自独立计入。
5. 评论文字为空时提交按钮不可点击；含图片但仍要求文字非空。
6. 评论提交成功后，评论出现在列表顶部，且自带删除按钮。
7. 切换到另一浏览器再看同一评论，无删除按钮。
8. 评论删除接口对其他 anon_id 返回 403；带图片的评论删除后，对应文件不再存在于 uploads 下。
9. 后端 pytest 全绿，前端 Vitest 全绿，`docker compose build` 成功。

---

## 10. 风险与未决问题

- **匿名 ID 易伪造**：明显可由前端篡改。作业范围内可接受，REFLECTION 中需声明。
- **SQLite 没有原生 ON DELETE CASCADE 默认开启**：本期帖子不实现删除，因此外键级联不会真正触发；预留路径。
- **图片存储目录权限**：与发帖共用 `NJU_UPLOAD_DIR`，无新增风险。
- **测试中 `X-Anon-Id` UUID 校验**：需要测试用例覆盖空、非法、合法三种情况。
