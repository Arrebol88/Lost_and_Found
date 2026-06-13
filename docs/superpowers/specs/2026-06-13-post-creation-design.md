# 南哪寻宝 · 发帖功能设计规格（SPEC）

- **项目名称**：南哪寻宝（南京大学失物招领网站）
- **本规格范围**：发帖闭环（首页发帖按钮 → 类型选择 → 表单 → 提交入库）
- **创建日期**：2026-06-13
- **作者**：项目所有者 + Superpowers 协作

---

## 1. 问题陈述

南京大学校园内频繁发生物品丢失与捡拾，但缺少一个**面向南大学生、轻量、零登录门槛**的失物招领信息汇集平台。现有渠道（QQ 群、各院系公众号）信息零散、检索困难、不分类。

**目标用户**：南京大学全体在校学生（含本科生、研究生）。
**为什么值得做**：低门槛（不登录直接发帖）+ 集中信息源 + 分类清晰 → 显著提升找回率。

本期范围：**只实现"发帖"这一最小完整链路**，列表 / 详情 / 搜索留待后续迭代。

## 2. 用户故事（INVEST）

1. **US-1**：作为捡到物品的同学，我希望点首页"发帖"→选"我捡到了东西"→填写信息→提交，整个过程一次完成，不需要注册登录。
2. **US-2**：作为丢失物品的同学，我希望同一个发帖入口选"我丢了东西"，填写信息（含我的联系方式）后即刻发布。
3. **US-3**：作为发帖人，我希望能上传一张物品图片，让看到帖子的人更容易辨认。
4. **US-4**：作为发帖人，我希望必填项缺失或格式错误时被立刻提示，而不是提交后才报错。
5. **US-5**：作为捡到物品的同学，我希望可以选择"自取/联系我/已移交管理处"三种交付方式之一，并写明具体安排。

## 3. 功能规约

### 3.1 首页

- **输入**：无
- **行为**：渲染一个居中"发帖"按钮
- **输出**：点击后进入类型选择视图
- **错误处理**：N/A

### 3.2 类型选择

- **输入**：用户点击"我捡到了东西（寻主帖）"或"我丢了东西（寻物帖）"
- **行为**：携带 `post_type ∈ {found, lost}` 进入表单
- **输出**：渲染对应表单
- **取消**：可返回首页

### 3.3 发帖表单

- **输入字段**（详见 §6 数据模型）：
  - 物品名称 *（作为帖子标题）
  - 物品种类 *（9 项枚举）
  - 物品图片（单张，可空）
  - 物品描述（≤500 字，可空）
  - 丢失/捡到地点 *
  - 丢失/捡到时间 *（精确到分钟）
  - 联系方式 *（按 post_type 分支，见下）
- **行为**：
  - 前端先做必填、长度、时间范围、图片类型与大小校验
  - 通过后以 `multipart/form-data` 提交至 `POST /api/posts`
- **输出**：
  - 成功：toast"发布成功"，回到首页
  - 失败：toast 显示后端返回的 `detail`
- **边界条件**：
  - 标题 1–50 字
  - 描述 ≤ 500 字
  - 地点 1–100 字
  - 联系方式描述 1–200 字
  - 时间不晚于当前、不早于当前 - 1 年
  - 图片：jpg/jpeg/png/webp，≤ 5MB，单张

### 3.4 联系方式分支规则

| post_type | 可选 contact_type | UI 表现 |
|---|---|---|
| `lost`（寻物帖） | 仅 `owner_contact` | 直接展示"联系方式"文本框，自动绑定 type |
| `found`（寻主帖） | `self_pickup` / `contact` / `handed_over` 三选一 | 单选 + 描述文本框 |

后端在收到请求时再次校验该规则；不匹配 → 400。

## 4. 非功能性需求

- **性能**：单次发帖端到端 < 2s（不含图片网络耗时）
- **安全**：
  - 图片双重校验（MIME + magic bytes），防止可执行文件伪装
  - 所有文本字段长度上限，防 DoS
  - 不包含登录态，但同一 IP 1 分钟最多发 5 帖（**本期只在 SPEC 中列出，作为风险标注，不强制实现**）
- **可用性**：移动端浏览器友好（响应式表单）
- **可观测性**：FastAPI 默认日志 + 关键路径打印 INFO（创建 post 成功 / 失败原因）

## 5. 系统架构

```
浏览器 (Vue 3 + Vite, :5173)
   │  axios multipart/form-data
   ▼
FastAPI (uvicorn, :8000)
   ├─ /api/health         → 健康检查
   ├─ /api/posts (POST)   → 创建帖子（含图片）
   └─ /uploads/* (static) → 静态图片访问
        │
        ├─→ uploads/YYYY/MM/DD/<uuid>.<ext>   （文件系统）
        └─→ SQLite: posts 表                  （sqlite3 文件）
```

外部依赖：无（SQLite 内嵌、图片本地存储）。

## 6. 数据模型

### 表 `posts`

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `id` | INTEGER | PK AUTOINCREMENT | 主键 |
| `post_type` | TEXT | NOT NULL, CHECK in (`found`,`lost`) | 帖子类型 |
| `title` | TEXT | NOT NULL, 长度 1–50 | 物品名称（兼帖子标题）|
| `category` | TEXT | NOT NULL, CHECK in 9 枚举 | 物品分类 |
| `image_path` | TEXT | NULL | 形如 `uploads/2026/06/13/<uuid>.jpg` |
| `description` | TEXT | NULL, 长度 ≤ 500 | 物品描述 |
| `location` | TEXT | NOT NULL, 长度 1–100 | 丢失/捡到地点 |
| `event_time` | DATETIME | NOT NULL | 不晚于 now，不早于 now-1 年 |
| `contact_type` | TEXT | NOT NULL, CHECK in 4 枚举 | 见 §3.4 |
| `contact_detail` | TEXT | NOT NULL, 长度 1–200 | 联系/交付方式具体说明 |
| `created_at` | DATETIME | NOT NULL, default CURRENT_TIMESTAMP | 服务端写入 |

### 枚举

- `category`（中文 ↔ 英文短码）：
  - 电子产品类 → `electronics`
  - 个人证件与卡类 → `id_card`
  - 箱包与收纳 → `bag`
  - 配饰 → `accessory`
  - 衣物 → `clothing`
  - 日常小件 → `daily`
  - 办公与学习 → `study`
  - 运动与户外 → `sports`
  - 个人护理与健康 → `personal_care`
- `contact_type`：`self_pickup` / `contact` / `handed_over` / `owner_contact`

### 业务约束（DB CHECK + 应用层 Pydantic 双层）

- `post_type='lost'` ⇒ `contact_type='owner_contact'`
- `post_type='found'` ⇒ `contact_type ∈ {self_pickup, contact, handed_over}`

## 7. API 设计

### 7.1 `POST /api/posts`

请求：`multipart/form-data`

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `post_type` | string | ✅ | `found` / `lost` |
| `title` | string | ✅ | 1–50 字 |
| `category` | string | ✅ | 见枚举 |
| `description` | string | ❌ | ≤500 字 |
| `location` | string | ✅ | 1–100 字 |
| `event_time` | string (ISO 8601) | ✅ | 形如 `2026-06-13T14:30` |
| `contact_type` | string | ✅ | 见枚举，需与 post_type 匹配 |
| `contact_detail` | string | ✅ | 1–200 字 |
| `image` | file | ❌ | jpg/jpeg/png/webp, ≤5MB |

成功响应（201）：
```json
{
  "id": 1,
  "post_type": "found",
  "title": "黑色雨伞",
  "category": "daily",
  "image_path": "uploads/2026/06/13/8f...c1.jpg",
  "description": "长柄，伞骨弯了一根",
  "location": "鼓楼校区逸夫楼 B201",
  "event_time": "2026-06-12T18:30:00",
  "contact_type": "self_pickup",
  "contact_detail": "工作日 8:00-17:00 在生活委员处自取",
  "created_at": "2026-06-13T10:00:00"
}
```

错误响应：
- `400`：`{ "detail": "<具体原因，中文>" }`（字段缺失、枚举非法、时间越界、contact 与 type 不匹配、图片格式错误）
- `413`：图片超过 5MB

### 7.2 `GET /api/health`

返回 `{ "status": "ok" }`，用于 Docker healthcheck 与冷启动验证。

### 7.3 `GET /uploads/*`

由 FastAPI `StaticFiles` 挂载，返回原图（用于后续详情页）。

## 8. 技术选型与理由

| 层 | 选型 | 理由 |
|---|---|---|
| 后端 | Python 3.11 + FastAPI | 用户指定；类型注解 + Pydantic 校验天然契合 SPEC 驱动 |
| ORM | SQLAlchemy 2.x | FastAPI 主流搭档，便于后续迁移 PG |
| DB | SQLite（WAL） | 用户指定；零运维；本作业规模够用 |
| 图片存储 | 本地 `uploads/` + DB 存路径 | 用户指定 |
| 前端 | Vue 3（Composition API）+ Vite | 用户指定；Vite 启动快 |
| HTTP | axios | 与 multipart 协作成熟 |
| 测试 | 后端 pytest + httpx；前端 Vitest + @vue/test-utils | 主流、CI 友好 |
| 容器 | 双 Dockerfile + docker-compose | 一键启动满足作业要求 |
| CI | GitHub Actions | 作业要求 |

**Open Design 适用性**：本期范围只有发帖表单，不涉及营销页/仪表盘等复杂界面。前端使用简洁的原生 Vue 组件 + 朴素 CSS，参考 Linear / Notion 的极简表单风格（留白充足、字段间距 16–24px、主色 `#0f172a` + 强调色 `#2563eb`）。后续若扩展首页列表 / 详情页将引入 Open Design 的 `dashboard` 或 `landing` skill。

## 9. 验收标准

1. `docker compose up` 后访问 `http://localhost:5173` 看到首页发帖按钮。
2. 完成 4 条端到端提交（寻物帖无图 1 条 + 寻主帖三种 contact_type 各 1 条），均返回 201。
3. SQLite `posts` 表中 4 条记录字段正确；`uploads/` 下出现对应图片，DB 路径与文件路径一致。
4. 后端 pytest 全部用例（含 §10 测试要点）红 → 绿。
5. 前端 Vitest 关键组件用例通过。
6. 仓库根目录 `make test`（或等价命令）一键跑通后端 + 前端测试。
7. GitHub Actions CI 通过：lint + test + 构建两个 Docker 镜像。
8. 后端 `/api/health` 在容器启动 15s 内返回 200。

## 10. 测试要点（TDD 红绿先行）

后端关键用例：
- `test_health_ok`
- `test_create_lost_post_no_image_201`
- `test_create_found_post_with_jpg_201_and_file_persisted`
- `test_reject_lost_with_non_owner_contact_400`
- `test_reject_found_with_owner_contact_400`
- `test_reject_missing_title_400`
- `test_reject_invalid_category_400`
- `test_reject_event_time_in_future_400`
- `test_reject_event_time_older_than_one_year_400`
- `test_reject_image_over_5mb_413`
- `test_reject_image_with_fake_extension_400`（magic bytes 校验）
- `test_title_length_boundary_50_ok_51_400`
- `test_db_failure_cleans_up_uploaded_file`（孤儿图片防御）

前端关键用例：
- `TypePicker` 两种 emit
- `PostForm` 必填校验
- `PostForm` 按 `post_type` 渲染联系方式分支
- `PostForm` 提交时构造的 FormData 字段正确
- 时间控件 min/max 边界

## 11. 风险与未决问题

| 编号 | 风险 | 缓解 |
|---|---|---|
| R1 | 时区混乱 | 统一用本地时间字符串（中国学生场景），不做 UTC 转换 |
| R2 | 孤儿图片（写文件成功但写 DB 失败） | 流程：先写文件 → 再写 DB；DB 失败时同步删除文件；含一条专门测试 |
| R3 | 滥发帖（无登录） | 本期不实现限频；SPEC 标注为已知风险，后续迭代加 IP 限频 |
| R4 | SQLite 写并发 | 启用 WAL 模式；本作业规模无瓶颈 |
| R5 | 图片伪装攻击 | MIME + magic bytes 双校验 |
| R6 | 前端 datetime-local 在 Safari 旧版表现差 | 提示用户使用 Chrome/Edge/移动端最新浏览器 |

## 12. 与作业要求对应

- **3000–8000 行**：本 SPEC 仅覆盖第一个 worktree/PR，后续列表、详情、搜索、管理后台扩展将累计达成此范围。
- **Docker 化**：满足，含 docker-compose。
- **TDD**：所有功能先测试再实现。
- **冷启动验证**：在 PLAN 完成后用第二个 agent 仅凭 SPEC + PLAN 跑 1–2 个 task，结果记入 `SPEC_PROCESS.md`。
