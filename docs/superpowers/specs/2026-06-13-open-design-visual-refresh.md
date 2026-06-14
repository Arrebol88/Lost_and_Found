# 设计：基于 Open Design 方法论的前端视觉重构（亮色 / Notion 取向）

> 状态：已确认  
> 创建日期：2026-06-13  
> 范围：仅前端视觉层与样式 token；不改后端、不改业务逻辑、不改测试断言文本

## 1. 问题陈述

现有前端（10 个 Vue 组件）每个都各自写 scoped CSS，没有统一的色彩、字号、间距 token，
颜色（蓝、灰、红）散落在各文件中，hover/focus 风格不一致，整体观感"AI 直出 demo"。
本次改造要把视觉收敛到一份品牌契约（`DESIGN.md` + `tokens.css`），
重点打磨**首页（PostList + PostFilters + PostCard）**与**帖子详情页（PostDetail + 评论区）**，
让站点呈现 Notion 风的暖灰、克制、阅读优先气质。

为什么值得做：本作业明文要求"凡涉及 UI 的项目使用 Open Design"。
本会话内 Open Design 桌面 daemon 未在 PATH，无法启动其 CLI/MCP 工具；
故采用方法论替代：仿照 Open Design 的 `DESIGN.md` 品牌契约 + 5 维反 AI-slop 自评 + P0/P1/P2 验收清单，
手工把规范落到 Vue 组件。该偏离会在 `AGENT_LOG.md` 记录。

## 2. 用户故事

1. 作为访客，我打开首页能在 5 秒内看清页面三件事：站名、当前看的是寻物还是招领、最近的几条帖子。
2. 作为访客，筛选条件清晰可见，并且明确知道"当前是否有筛选生效"。
3. 作为访客，我点开任一帖子详情页，眼睛能轻松找到"标题 → 元信息 → 描述 → 联系方式 → 互动"五个层级。
4. 作为帖主，详情页的编辑/删除按钮明确但不抢戏，删除有 hover 提示色。
5. 作为读者，评论区与正文层级分明，自己发的评论可以在 hover 时看到删除入口。

## 3. 功能规约（按页面拆分）

### 3.1 全局基底

- 顶部背景为 `--bg`（`#FAF9F7`），不再使用纯白。
- 全局字体栈：`-apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", "Segoe UI", sans-serif`。
- 行高：正文 1.6，标题 1.3。
- 所有按钮、输入框、卡片**禁止使用** scoped 内硬编码色值，统一引用 `tokens.css` 的 CSS 变量。

### 3.2 列表页（首页）

| 区块 | 行为 / 视觉 |
|---|---|
| Hero | 左：`--fz-display` 站名 + `--fz-meta` 简介；右：主操作"我要发帖"+ 次操作"刷新"。 |
| TypePicker | 分段 chips：选中态 `--accent` 文字 + `--surface-2` 底；未选中 `--text-3`。 |
| 筛选栏 | `--surface-2` 长条容器（无边框），内部 chip 形态："分类: 全部 ▾"等。空筛选默认显示"全部"。 |
| 卡片网格 | 桌面 ≥ 1024px：3 列；640–1023：2 列；< 640：1 列。卡片用 `--shadow-card`，hover `translateY(-2px)` + `--shadow-pop`。 |
| 卡片内 | 图（4:3 cover）→ 类型 chip → 标题（最多 2 行省略）→ meta（地点 · 相对时间）。 |
| 空状态 | 暖灰虚线方框 + "暂时还没有匹配的帖子"。不使用插画。 |

### 3.3 详情页

| 区块 | 行为 / 视觉 |
|---|---|
| 容器 | `max-width: 720px`，居中，左右 24px padding。 |
| 顶部 bar | 左侧"← 返回"，右侧（仅 `mine`）"编辑"+"删除"。删除按钮 hover 才转 `--danger` 文字色。 |
| 标题区 | `--fz-display` 标题；下一行 meta：类型 chip + 地点 + 时间。 |
| 正文 | `--fz-body`，行高 1.7。描述自然展开，不加"展开"按钮。 |
| 联系方式 | 默认折叠为虚线方框 + "查看联系方式"；展开后 `--surface-2` 卡片展示。 |
| 点赞条 | 横置一条：♥ + 数字。已点 `--accent` 实色，未点 `--text-3`。点击切换。 |
| 评论区 | "评论 · N 条" `--fz-h2`。CommentForm 用 `--surface-2` 包裹；评论项之间 `--border` 1px 极细线；删除按钮 hover 才出现。 |

### 3.4 表单页（PostForm / PostEdit / CommentForm）

不在本期重点重构，但要：

- 引用 `tokens.css` 替换硬编码色（蓝色 `#2563eb` → `var(--accent)`）。
- 输入框统一 `--surface` + `--border-strong` 描边，focus 时 `--accent` 描边 + 1px 浅色 ring。
- 主按钮统一 `--accent` 实色；次按钮 `--surface-2` 实色 + `--border-strong` 描边。

## 4. 非功能性需求

- **性能**：CSS 仅引入一个 `tokens.css`（≤ 2 KB gzip）；不引入 UI 库。
- **可访问性**：所有交互元素 `:focus-visible` 必有可见焦点环（`--accent` 1px ring）。
- **响应式**：≤ 480px 网格 1 列，详情页留白收紧到 16px padding。
- **i18n**：仅简体中文；中英混排时保留 ASCII 标点不替换。

## 5. 系统架构（前端层）

```
frontend/src/
├── styles/
│   └── tokens.css           ← 新增，CSS variables：色 / 字号 / 间距 / 阴影 / 圆角
├── main.js                  ← 引入 tokens.css
├── App.vue                  ← 重构：Hero、TypePicker chip
├── components/
│   ├── PostList.vue         ← 重构：网格布局
│   ├── PostFilters.vue      ← 重构：chip 形态
│   ├── PostCard.vue         ← 重构：卡片节奏
│   ├── PostDetail.vue       ← 重构：阅读栏 + 顶部 bar
│   ├── CommentForm.vue      ← 收敛：色 token 化
│   ├── CommentList.vue      ← 收敛：分隔线 + hover 删除
│   ├── PostForm.vue         ← 收敛：色 token 化（不做大改）
│   ├── PostEdit.vue         ← 收敛：色 token 化（不做大改）
│   └── TypePicker.vue       ← 重构：chip
DESIGN.md                    ← 新增，品牌契约（人类阅读）
```

## 6. 数据模型

无后端字段变更。

## 7. API 设计

无后端接口变更。

## 8. 技术选型与理由

- **不引入 UI 库**：作业明确要求避免"AI-slop"；UI 库的默认风格反而会拉平品牌特征。Notion 风靠 token + 节奏即可达到，不必依赖组件库。
- **CSS 变量而非 SCSS**：变量在浏览器运行期生效，便于将来加暗色模式只需替换根级变量；项目已有 vite，原生 CSS 变量足矣。
- **不引入 icon 库**：用内联 SVG 或字符（♥ ←）替代，避免 800+ KB 依赖。
- **Open Design**：方法论遵循（`DESIGN.md` + 5 维 + P0/P1/P2），但不调用其 daemon/CLI；此偏离已声明。

## 9. 验收标准

P0（必须达成 / 阻塞合并）：

- `frontend/src/styles/tokens.css` 创建，且被 `main.js` 引入。
- `DESIGN.md` 落到仓库根。
- 所有列表页与详情页相关组件不再出现非 token 颜色字面量（`#xxx`、`rgb(...)`）。
- `npm test --silent` 全绿、`npm run build` 成功、`docker compose build` 成功。

P1（应达成）：

- 移动端 ≤ 480px 列表 1 列、详情页正文左右 padding ≤ 16px。
- 所有交互元素 `:focus-visible` 出现 `--accent` 焦点环。
- 5 维自评每项不低于 3 分（自评表落到本 SPEC 末尾）。

P2（可选）：

- 评论附件缩略改为 56×56 圆角。
- 详情页折叠区 200ms ease-out 动效。

## 10. 风险与未决问题

- **现有 vitest 是否依赖类名硬断言**：每个组件改造前会先 grep 对应测试，必要时同步调整选择器（保持行为断言不变）。
- **中文字体在不同操作系统下的回退**：依赖系统字体栈，不引入 webfont，规避加载阻塞。
- **token 滥用风险**：若 token 不够细，临时引入新 token 而非临时硬编码颜色；本期固定 token 表已列出。

## 11. 5 维反 AI-slop 自评（实施后填写）

| 维度 | 列表页 | 详情页 | 检查点 |
|---|---|---|---|
| 信息层级 | 4 | 5 | 列表卡片只渲染 cover/tag/title/meta 四块，且 title 用 600 + 大字号；详情页"标题 → meta → 描述 → 联系方式 → 互动"五个层级各自独立。 |
| 间距节奏 | 5 | 5 | 全部 padding/gap/margin 引用 4/8/12/16/24/32 台阶 token；扫描组件 scoped style 已无奇数像素。 |
| 排版克制 | 5 | 5 | 仅使用 fz-display/h2/body/meta/mini 五档；字重只用 400/600。 |
| 色彩克制 | 4 | 4 | 全站只使用 `--accent`、`--text-1/2/3`、`--surface`/`--surface-2`、`--border`/`--border-strong`、`--lost-tag-*`/`--found-tag-*` 与 `--danger` hover；不出现 `#000`/`#FFF`。 |
| 中文细节 | 4 | 4 | 中英文字符混排时使用 0.5em 间距 dot；按钮文本无中英标点混用；description 使用 word-break: break-word。 |

实施后所有维度 ≥ 4，全部 P0 达成。
