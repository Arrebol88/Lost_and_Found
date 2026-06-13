# 南哪寻宝 · 帖子展示与过滤功能设计规格（SPEC）

- **项目名称**：南哪寻宝（南京大学失物招领网站）
- **本规格范围**：地点枚举化、寻主帖联系方式文案调整、首页帖子展示、底部寻物 / 寻主导航、顶部三项过滤器
- **创建日期**：2026-06-13
- **作者**：项目所有者 + Superpowers 协作

---

## 1. 问题陈述

当前系统已经完成发帖闭环，但首页只能发帖，用户无法浏览已有失物招领信息。为了让南京大学学生能够快速查看和筛选相关帖子，本轮新增首页帖子展示功能，并将发帖地点从自由文本改为校区选择，减少地点输入不一致带来的过滤困难。

**目标用户**：南京大学丢失物品或捡到物品的学生。

**为什么值得做**：

- 浏览帖子是失物招领平台的核心能力。
- 校区枚举化可以让过滤器可靠工作。
- 顶部过滤器降低信息噪音，帮助用户快速定位相关帖子。
- 底部「寻物 / 寻主」导航让两类帖子入口清晰。

## 2. 用户故事（INVEST）

1. **US-1**：作为丢失物品的学生，我希望进入网站后默认看到「寻物」页面，以便查看其他失主发布的寻物帖。
2. **US-2**：作为捡到物品的学生，我希望通过底部「寻主」导航查看捡到物品的人发布的帖子，方便确认是否有人捡到相关物品。
3. **US-3**：作为浏览者，我希望按物品种类、时间范围和校区过滤帖子，减少无关信息。
4. **US-4**：作为发帖人，我希望发帖时从固定校区中选择地点，避免地点写法不统一。
5. **US-5**：作为捡到物品的发帖人，我希望寻主帖的联系方式描述字段文案更明确，知道这里应填写联系方式相关的具体说明。

## 3. 功能规约

### 3.1 发帖地点字段改造

- **输入**：用户在发帖表单中选择校区。
- **行为**：`location` 从自由文本输入改为下拉选择。
- **输出**：提交到后端的 `location` 为枚举短码。
- **可选项**：
  - 鼓楼校区 → `gulou`
  - 仙林校区 → `xianlin`
  - 苏州校区 → `suzhou`
  - 浦口校区 → `pukou`
- **错误处理**：前端未选择时提示「请选择地点」；后端收到非法地点时返回 400。

### 3.2 寻主帖联系方式文案调整

- **现状**：寻主帖联系方式选项下方文本域 label 为「具体描述 *」。
- **修改后**：寻主帖文本域 label 为「联系方式具体描述 *」。
- **寻物帖不变**：仍显示「联系方式 *」。
- **数据模型不变**：仍提交到 `contact_detail` 字段。

### 3.3 首页帖子展示

- **默认页面**：进入网站默认展示「寻物」Tab，即 `post_type = lost`。
- **底部导航**：
  - 「寻物」：展示失主发布的寻物帖，对应 `post_type = lost`。
  - 「寻主」：展示捡到物品的人发布的寻主帖，对应 `post_type = found`。
- **发帖入口**：保留发帖按钮，放在列表页中显眼位置；点击后沿用现有类型选择和发帖表单流程。
- **卡片展示字段**：
  - 标题（`title`）
  - 校区地点（`location` 的中文显示）
  - 丢失 / 捡到时间（`event_time`，格式化为 `YYYY-MM-DD HH:mm`）
  - 首图缩略图（若 `image_path` 存在）
- **不做内容**：本轮不做详情页，不展示联系方式，不展示完整描述，卡片不可点击。

### 3.4 顶部过滤器

首页顶部提供 3 个过滤器，均有「全部」默认项。

| 过滤器 | 选项 | 请求参数 |
|---|---|---|
| 物品种类 | 全部 + 9 类物品种类 | `category` |
| 丢失 / 捡到时间 | 全部、一天以内、三天以内、七天以内、七天以外 | `time_range` |
| 丢失 / 捡到地点 | 全部、鼓楼校区、仙林校区、苏州校区、浦口校区 | `location` |

过滤器默认值为空字符串，表示不过滤。切换「寻物 / 寻主」Tab 时保留过滤器状态。

### 3.5 发帖成功后的列表刷新

- 发帖成功后回到首页。
- 自动切换到刚发布帖子对应的 Tab。
- 重新请求列表，确保新帖子立即出现。

## 4. 非功能性需求

- **性能**：列表接口默认最多返回 50 条，最大 100 条；首页首屏请求应在 1 秒内完成（本地环境）。
- **隐私**：列表 API 不返回 `contact_detail`，首页不展示联系方式。
- **可用性**：底部导航适配移动端；过滤器在窄屏下纵向排列。
- **一致性**：前后端共享同一组枚举语义；数据库、Pydantic、前端 select 选项保持一致。

## 5. 系统架构与数据流

```text
浏览器 Vue 首页
  ├─ 默认 activeTab = lost
  ├─ 顶部过滤器生成 query params
  └─ GET /api/posts?post_type=lost&category=&location=&time_range=
        ↓
FastAPI posts router
  ├─ 校验 post_type / category / location / time_range
  ├─ 构造 SQLAlchemy 查询条件
  ├─ 按 created_at desc 排序
  └─ 返回列表卡片所需字段
        ↓
Vue PostList / PostCard 渲染标题、校区、时间、缩略图
```

## 6. 数据模型

现有 `posts.location` 字段保持为 `String(100)`，但语义改为校区枚举。

新增地点枚举：

| 字段值 | 中文显示 |
|---|---|
| `gulou` | 鼓楼校区 |
| `xianlin` | 仙林校区 |
| `suzhou` | 苏州校区 |
| `pukou` | 浦口校区 |

数据库层新增 CHECK 约束：

```sql
location IN ('gulou', 'xianlin', 'suzhou', 'pukou')
```

应用层新增 `CampusLocation` 枚举，并用于 `PostCreate`、列表查询参数校验和响应模型。

## 7. API 设计

### 7.1 修改 `POST /api/posts`

`location` 字段仍为必填，但只能传以下值：

```text
gulou | xianlin | suzhou | pukou
```

非法值返回 400。

### 7.2 新增 `GET /api/posts`

#### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `post_type` | `lost` / `found` | 是 | 无 | 当前底部 Tab |
| `category` | 9 类枚举 | 否 | 无 | 不传或空字符串表示全部 |
| `location` | `gulou` / `xianlin` / `suzhou` / `pukou` | 否 | 无 | 不传或空字符串表示全部 |
| `time_range` | `within_1d` / `within_3d` / `within_7d` / `older_than_7d` | 否 | 无 | 不传或空字符串表示全部 |
| `limit` | integer | 否 | 50 | 最大 100 |
| `offset` | integer | 否 | 0 | 用于后续分页 |

#### 时间过滤语义

时间过滤基于 `event_time`，不是 `created_at`。

| 参数值 | 语义 |
|---|---|
| `within_1d` | `event_time >= now - 1 day` |
| `within_3d` | `event_time >= now - 3 days` |
| `within_7d` | `event_time >= now - 7 days` |
| `older_than_7d` | `event_time < now - 7 days` |

#### 成功响应

返回数组，按 `created_at desc` 排序。

```json
[
  {
    "id": 12,
    "post_type": "lost",
    "title": "黑色耳机",
    "category": "electronics",
    "image_path": "uploads/2026/06/13/xxx.jpg",
    "location": "xianlin",
    "event_time": "2026-06-13T15:30:00",
    "created_at": "2026-06-13T16:00:00"
  }
]
```

#### 响应字段限制

列表响应不返回以下字段：

- `description`
- `contact_type`
- `contact_detail`

## 8. 前端设计

### 8.1 组件结构

```text
App.vue
├── PostFilters.vue
├── PostList.vue
│   └── PostCard.vue
├── TypePicker.vue
└── PostForm.vue
```

### 8.2 组件职责

- `PostFilters.vue`：渲染 3 个过滤器，负责向父组件发出过滤条件变化。
- `PostList.vue`：处理 loading、error、empty 三种列表状态。
- `PostCard.vue`：只展示标题、校区、时间和缩略图。
- `PostForm.vue`：地点改为 select；寻主帖 label 改为「联系方式具体描述 *」。
- `api.js`：新增 `listPosts(filters)`。

### 8.3 状态规则

- `activeTab` 默认值为 `lost`。
- `filters` 默认值为：`{ category: '', time_range: '', location: '' }`。
- 切换 Tab 时保留 `filters`。
- 任一过滤器变化后重新请求列表。
- 发帖成功后切换到新帖对应 Tab 并刷新列表。

### 8.4 图片 URL

后端返回 `image_path` 相对路径。前端展示时拼接后端地址：

- 开发态：通过 Vite 代理访问 `/uploads/...`。
- 生产态：拼接 `http://localhost:8000/${image_path}`。

## 9. 测试策略（TDD）

### 9.1 后端 pytest 新增用例

- `test_create_post_rejects_free_text_location`
- `test_create_post_accepts_campus_location`
- `test_list_posts_requires_post_type`
- `test_list_posts_filters_by_post_type`
- `test_list_posts_filters_by_category`
- `test_list_posts_filters_by_location`
- `test_list_posts_filters_by_time_range`
- `test_list_posts_excludes_contact_detail`
- `test_list_posts_limit_max_100`

### 9.2 前端 Vitest 新增用例

- `PostForm` 地点字段是 select，且包含 4 个校区。
- 寻主帖 label 显示「联系方式具体描述 *」。
- `api.listPosts` 正确传递过滤参数。
- `PostFilters` 三个过滤器默认显示「全部」。
- `PostCard` 只展示标题、校区、时间和图片，不展示联系方式。
- `App` 默认请求 `post_type=lost`。
- 切换底部导航后请求 `post_type=found`。

## 10. 验收标准

1. 进入网站默认展示「寻物」Tab。
2. 首页底部有两个导航项：「寻物」和「寻主」。
3. 顶部 3 个过滤器均包含「全部」默认项。
4. 发帖表单中「丢失 / 捡到地点」只能选择 4 个校区。
5. 寻主帖联系方式下方 label 是「联系方式具体描述 *」。
6. 发布寻物帖后，首页寻物列表出现对应卡片。
7. 发布寻主帖后，首页寻主列表出现对应卡片。
8. 物品种类、时间范围、校区 3 个过滤器可以组合过滤列表。
9. 卡片只展示标题、校区地点、丢失 / 捡到时间、图片缩略图（如有）。
10. `make test` 全部通过。
11. Docker 构建和 `docker compose up` 仍可正常运行。

## 11. 风险与处理

| 编号 | 风险 | 处理 |
|---|---|---|
| R1 | 旧数据库中已有自由文本 `location`，新增 CHECK 后可能不兼容 | 本项目仍处早期开发，允许重建 SQLite；README 补充如需重置数据库可删除本地 DB / Docker volume |
| R2 | 列表不展示联系方式，用户无法直接联系 | 本轮按用户指定只做卡片展示；详情页作为后续迭代 |
| R3 | 过滤器组合后结果为空，用户误以为加载失败 | 空状态明确显示「暂无寻物帖」或「暂无寻主帖」 |
| R4 | 时间过滤边界不一致 | 后端统一以服务器当前时间计算，前端只传 time_range 枚举 |
| R5 | 图片路径在开发态和生产态不同 | 统一封装 `imageUrl()`，避免组件内硬编码 |

## 12. 与既有规格的关系

本规格是 `2026-06-13-post-creation-design.md` 的后续迭代，保留原有发帖闭环、图片上传、SQLite 存储、Docker 和 CI 设计，仅扩展列表查询、首页展示和地点枚举校验。
