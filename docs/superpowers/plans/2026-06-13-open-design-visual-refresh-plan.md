# Open Design 风格视觉重构 实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 将首页（PostList + PostFilters + PostCard + TypePicker + App.vue）与详情页（PostDetail + CommentForm + CommentList）的视觉收敛到 `frontend/src/styles/tokens.css` 的 token，并补齐表单页（PostForm / PostEdit）的 token 化。

**架构：** 新增 `tokens.css` 在 `main.js` 中全局引入，每个 Vue 组件 scoped style 内部仅引用 `var(--token)`，禁止硬编码色值。逐组件改造，每个组件作为一个独立任务，TDD 节奏：先 grep/调整既有 vitest，再改 style，再跑 `npm test --silent` 与 `npm run build` 确认绿。

**技术栈：** Vue 3 SFC + 原生 CSS variables（不引入 Tailwind / SCSS / 任何 UI 库 / 任何 icon 库）。

---

## 文件清单

- 创建：`frontend/src/styles/tokens.css`
- 修改：`frontend/src/main.js`（增加 `import './styles/tokens.css'`）
- 修改：`frontend/src/App.vue`、`PostList.vue`、`PostFilters.vue`、`PostCard.vue`、`TypePicker.vue`、`PostDetail.vue`、`CommentForm.vue`、`CommentList.vue`、`PostForm.vue`、`PostEdit.vue`
- 不改：`frontend/tests/**`（行为断言不动；如某个测试断言到具体 class 字符串导致破，再做最小同步调整并在该任务中说明）

---

### 任务 1：建立 tokens.css 与全局加载

**文件：**
- 创建：`frontend/src/styles/tokens.css`
- 修改：`frontend/src/main.js`

- [ ] **步骤 1：写 tokens.css**

```css
:root {
  --bg: #FAF9F7;
  --surface: #FFFFFF;
  --surface-2: #F3F1EC;
  --border: #E8E4DD;
  --border-strong: #D6D1C7;
  --text-1: #1F1B16;
  --text-2: #4A453E;
  --text-3: #857F76;
  --accent: #6B5BD2;
  --accent-hover: #5A4BC2;
  --danger: #C2410C;
  --warning: #B45309;
  --success: #15803D;
  --lost-tag-fg: #9A3412;
  --lost-tag-bg: #FEF3C7;
  --found-tag-fg: #166534;
  --found-tag-bg: #DCFCE7;

  --fz-display: 28px;
  --fz-h2: 20px;
  --fz-body: 15px;
  --fz-meta: 13px;
  --fz-mini: 12px;

  --sp-1: 4px;  --sp-2: 8px;  --sp-3: 12px;  --sp-4: 16px;
  --sp-5: 24px; --sp-6: 32px; --sp-7: 48px;

  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 14px;

  --shadow-card: 0 1px 2px rgba(31,27,22,.04), 0 1px 3px rgba(31,27,22,.06);
  --shadow-pop:  0 4px 16px rgba(31,27,22,.08);
}

html, body, #app {
  background: var(--bg);
  color: var(--text-2);
  font-family: -apple-system, BlinkMacSystemFont, "PingFang SC",
               "Microsoft YaHei", "Segoe UI", sans-serif;
  font-size: var(--fz-body);
  line-height: 1.6;
}

*, *::before, *::after { box-sizing: border-box; }

:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
  border-radius: var(--radius-sm);
}
```

- [ ] **步骤 2：main.js 引入**

```js
import { createApp } from 'vue'
import './styles/tokens.css'
import App from './App.vue'

createApp(App).mount('#app')
```

- [ ] **步骤 3：跑测试 + 构建**

运行：`npm test --silent` → 预期 38 passed  
运行：`npm run build --silent` → 预期成功

- [ ] **步骤 4：Commit**

```bash
git add frontend/src/styles/tokens.css frontend/src/main.js
git commit -m "feat(style): add design tokens and global styles"
```

---

### 任务 2：App.vue Hero 与 TypePicker 容器

**文件：** 修改 `frontend/src/App.vue`

- [ ] **步骤 1：grep 测试**

运行：`grep -n "data-testid\|class=" frontend/tests/App.test.js`  
预期：只断言 `data-testid="post-card"` 等行为节点。

- [ ] **步骤 2：替换 App.vue scoped style**

将 App 顶部包装结构改为 Hero（左标题 + 右操作按钮），用 token：

```vue
<style scoped>
.app { max-width: 1080px; margin: 0 auto; padding: var(--sp-6) var(--sp-5); }
.hero { display: flex; align-items: flex-end; justify-content: space-between; margin-bottom: var(--sp-6); }
.hero h1 { font-size: var(--fz-display); color: var(--text-1); margin: 0 0 var(--sp-2); font-weight: 600; }
.hero .sub { font-size: var(--fz-meta); color: var(--text-3); }
.hero .actions { display: flex; gap: var(--sp-3); }
.btn-primary { background: var(--accent); color: white; border: 0; padding: var(--sp-2) var(--sp-4); border-radius: var(--radius-sm); cursor: pointer; }
.btn-primary:hover { background: var(--accent-hover); }
.btn-ghost { background: var(--surface-2); color: var(--text-1); border: 1px solid var(--border-strong); padding: var(--sp-2) var(--sp-4); border-radius: var(--radius-sm); cursor: pointer; }
</style>
```

并把 template 顶部改为：

```vue
<header class="hero">
  <div>
    <h1>南大失物招领</h1>
    <div class="sub">校园丢失 / 拾得物匿名汇集</div>
  </div>
  <div class="actions" v-if="view === 'home'">
    <button class="btn-ghost" @click="loadPosts">刷新</button>
    <button class="btn-primary" @click="openCreate">我要发帖</button>
  </div>
</header>
```

仅保留现有 `view`/`openCreate`/`loadPosts` 等已存在函数；不动逻辑。

- [ ] **步骤 3：跑测试 + 构建**

运行：`npm test --silent && npm run build --silent`  
预期：38 passed + build 成功。

- [ ] **步骤 4：Commit**

```bash
git add frontend/src/App.vue
git commit -m "style(app): apply tokens to hero and global layout"
```

---

### 任务 3：TypePicker chip 化

**文件：** 修改 `frontend/src/components/TypePicker.vue`

- [ ] **步骤 1：grep 测试**

运行：`grep -n "data-testid\|class=" frontend/tests/TypePicker.test.js`  
确认仅断言 `data-testid="type-lost"` `data-testid="type-found"`。

- [ ] **步骤 2：替换样式**

```vue
<style scoped>
.picker { display: flex; gap: var(--sp-2); padding: var(--sp-1); background: var(--surface-2); border-radius: var(--radius-sm); width: fit-content; }
.picker button { background: transparent; border: 0; padding: var(--sp-2) var(--sp-4); font-size: var(--fz-meta); color: var(--text-3); cursor: pointer; border-radius: var(--radius-sm); transition: 160ms; }
.picker button.active { background: var(--surface); color: var(--accent); box-shadow: var(--shadow-card); }
.picker button:hover:not(.active) { color: var(--text-1); }
</style>
```

template 中保留 `data-testid` 与 `:class="{ active: ... }"` 不变。

- [ ] **步骤 3：测试 + 构建 + Commit**

运行：`npm test --silent && npm run build --silent`  
```bash
git add frontend/src/components/TypePicker.vue
git commit -m "style(type-picker): use token chip"
```

---

### 任务 4：PostFilters chip 行

**文件：** 修改 `frontend/src/components/PostFilters.vue`

- [ ] **步骤 1：grep 测试**

运行：`grep -n "data-testid\|class=" frontend/tests/PostListingComponents.test.js`  
确认行为断言不依赖样式 class。

- [ ] **步骤 2：替换 scoped style**

```vue
<style scoped>
.filters { display: flex; flex-wrap: wrap; gap: var(--sp-3); padding: var(--sp-3) var(--sp-4); background: var(--surface-2); border-radius: var(--radius-md); }
.field { display: inline-flex; align-items: center; gap: var(--sp-2); font-size: var(--fz-meta); color: var(--text-2); }
.field select { background: var(--surface); color: var(--text-1); border: 1px solid var(--border-strong); border-radius: var(--radius-sm); padding: var(--sp-1) var(--sp-3); font-size: var(--fz-meta); }
.field select:focus { border-color: var(--accent); outline: none; }
</style>
```

template：保持现有的 `data-testid="filter-category"` `filter-time` `filter-location` 等不变。

- [ ] **步骤 3：测试 + 构建 + Commit**

```bash
git add frontend/src/components/PostFilters.vue
git commit -m "style(filters): chip row on warm-grey strip"
```

---

### 任务 5：PostCard 网格卡片

**文件：** 修改 `frontend/src/components/PostCard.vue`

- [ ] **步骤 1：grep 测试**

运行：`grep -n "data-testid\|class=" frontend/tests/PostListingComponents.test.js frontend/tests/App.test.js`  
确认仅依赖 `data-testid="post-card"`、`alt="物品图片"` 等。

- [ ] **步骤 2：替换 scoped style**

```vue
<style scoped>
.card { display: flex; flex-direction: column; background: var(--surface); border-radius: var(--radius-md); box-shadow: var(--shadow-card); cursor: pointer; transition: 160ms ease-out; overflow: hidden; }
.card:hover { transform: translateY(-2px); box-shadow: var(--shadow-pop); }
.cover { aspect-ratio: 4 / 3; background: var(--surface-2); display: flex; align-items: center; justify-content: center; }
.cover img { width: 100%; height: 100%; object-fit: cover; display: block; }
.cover .placeholder { color: var(--text-3); font-size: var(--fz-meta); }
.body { padding: var(--sp-3) var(--sp-4) var(--sp-4); display: flex; flex-direction: column; gap: var(--sp-2); }
.tag { align-self: flex-start; padding: 2px var(--sp-2); border-radius: var(--radius-sm); font-size: var(--fz-mini); font-weight: 500; }
.tag.lost { background: var(--lost-tag-bg); color: var(--lost-tag-fg); }
.tag.found { background: var(--found-tag-bg); color: var(--found-tag-fg); }
.title { color: var(--text-1); font-size: var(--fz-body); font-weight: 600; line-height: 1.3; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.meta { color: var(--text-3); font-size: var(--fz-meta); display: flex; gap: var(--sp-2); }
.meta .dot { color: var(--border-strong); }
</style>
```

template：保持 `<article class="card" data-testid="post-card" @click="...">`，调整结构成 cover/body/tag/title/meta 节奏（缩略图、tag、title、地点 · 时间）。

- [ ] **步骤 3：测试 + 构建 + Commit**

```bash
git add frontend/src/components/PostCard.vue
git commit -m "style(post-card): warm card with grid-friendly anatomy"
```

---

### 任务 6：PostList 网格

**文件：** 修改 `frontend/src/components/PostList.vue`

- [ ] **步骤 1：grep 测试**

运行：`grep -n "data-testid\|class=" frontend/tests/App.test.js frontend/tests/PostListingComponents.test.js`  
确认 `data-testid="post-card"` 数组式存在。

- [ ] **步骤 2：替换 scoped style**

```vue
<style scoped>
.list { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: var(--sp-5); }
@media (max-width: 1024px) { .list { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 640px)  { .list { grid-template-columns: 1fr; gap: var(--sp-4); } }
.empty { padding: var(--sp-7) var(--sp-5); text-align: center; color: var(--text-3); font-size: var(--fz-meta); border: 1px dashed var(--border-strong); border-radius: var(--radius-md); }
</style>
```

template：根容器 `.list`，无数据时 `.empty` 显示"暂时还没有匹配的帖子"。

- [ ] **步骤 3：测试 + 构建 + Commit**

```bash
git add frontend/src/components/PostList.vue
git commit -m "style(post-list): responsive 3/2/1 grid with empty hint"
```

---

### 任务 7：PostDetail 阅读栏 + 顶部 bar

**文件：** 修改 `frontend/src/components/PostDetail.vue`

- [ ] **步骤 1：grep 测试**

运行：`grep -n "data-testid\|class=" frontend/tests/PostDetail.test.js frontend/tests/PostDetailEditDelete.test.js`  
确认仅依赖 `data-testid="post-edit"` `data-testid="post-delete"` `data-testid="like-btn"` 等。

- [ ] **步骤 2：替换 scoped style**

```vue
<style scoped>
.detail { max-width: 720px; margin: 0 auto; padding: var(--sp-5); }
.bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--sp-5); }
.back, .ghost, .danger { background: var(--surface); border: 1px solid var(--border-strong); padding: var(--sp-1) var(--sp-3); border-radius: var(--radius-sm); cursor: pointer; color: var(--text-2); font-size: var(--fz-meta); }
.danger:hover { color: var(--danger); border-color: var(--danger); }
.actions { display: flex; gap: var(--sp-2); }
.error { color: var(--danger); font-size: var(--fz-meta); margin-bottom: var(--sp-3); }
.post { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: var(--sp-6); }
.post h1 { font-size: var(--fz-display); color: var(--text-1); margin: 0 0 var(--sp-3); line-height: 1.3; }
.post .meta { color: var(--text-3); font-size: var(--fz-meta); display: flex; gap: var(--sp-3); margin-bottom: var(--sp-5); align-items: center; }
.tag { padding: 2px var(--sp-2); border-radius: var(--radius-sm); font-size: var(--fz-mini); font-weight: 500; }
.tag.lost { background: var(--lost-tag-bg); color: var(--lost-tag-fg); }
.tag.found { background: var(--found-tag-bg); color: var(--found-tag-fg); }
.image img { max-width: 100%; border-radius: var(--radius-md); margin-bottom: var(--sp-5); }
.desc { color: var(--text-2); white-space: pre-wrap; line-height: 1.7; margin-bottom: var(--sp-5); }
.contact { background: var(--surface-2); border-radius: var(--radius-md); padding: var(--sp-4); margin-bottom: var(--sp-5); }
.contact-toggle { display: inline-block; padding: var(--sp-2) var(--sp-4); border: 1px dashed var(--border-strong); border-radius: var(--radius-sm); color: var(--text-3); font-size: var(--fz-meta); cursor: pointer; }
.like-row { display: flex; align-items: center; gap: var(--sp-2); margin-top: var(--sp-4); padding-top: var(--sp-4); border-top: 1px solid var(--border); }
.like-btn { background: transparent; border: 0; cursor: pointer; font-size: 18px; color: var(--text-3); display: inline-flex; align-items: center; gap: var(--sp-1); }
.like-btn.liked { color: var(--accent); }
.like-count { color: var(--text-3); font-size: var(--fz-meta); }
.comments { margin-top: var(--sp-6); }
.comments h3 { font-size: var(--fz-h2); color: var(--text-1); font-weight: 600; margin: 0 0 var(--sp-4); }
</style>
```

template：在 `like-btn` 点亮态条件加 `:class="{ liked: post.liked_by_me }"`；联系方式默认隐藏并使用 `.contact-toggle` 链式按钮。

- [ ] **步骤 3：测试 + 构建 + Commit**

```bash
git add frontend/src/components/PostDetail.vue
git commit -m "style(post-detail): reading column with calm bar"
```

---

### 任务 8：CommentForm + CommentList token 化

**文件：** 修改 `frontend/src/components/CommentForm.vue`、`frontend/src/components/CommentList.vue`

- [ ] **步骤 1：grep 测试**

运行：`grep -n "data-testid\|class=" frontend/tests/CommentForm.test.js frontend/tests/CommentList.test.js`

- [ ] **步骤 2：CommentForm 样式**

```vue
<style scoped>
.form { background: var(--surface-2); border-radius: var(--radius-md); padding: var(--sp-4); display: flex; flex-direction: column; gap: var(--sp-3); margin-bottom: var(--sp-4); }
.form textarea { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-sm); padding: var(--sp-3); font: inherit; resize: vertical; min-height: 64px; }
.form textarea:focus { border-color: var(--accent); outline: none; }
.row { display: flex; justify-content: space-between; align-items: center; gap: var(--sp-3); }
.file { color: var(--text-3); font-size: var(--fz-meta); }
.submit { background: var(--accent); color: white; border: 0; padding: var(--sp-2) var(--sp-4); border-radius: var(--radius-sm); cursor: pointer; font-size: var(--fz-meta); }
.submit:disabled { background: var(--border-strong); cursor: not-allowed; }
.error { color: var(--danger); font-size: var(--fz-meta); }
</style>
```

- [ ] **步骤 3：CommentList 样式**

```vue
<style scoped>
.list { display: flex; flex-direction: column; }
.item { display: flex; gap: var(--sp-3); padding: var(--sp-4) 0; border-bottom: 1px solid var(--border); }
.item:last-child { border-bottom: 0; }
.item .body { flex: 1; }
.item .content { color: var(--text-2); white-space: pre-wrap; line-height: 1.7; }
.item .meta { color: var(--text-3); font-size: var(--fz-meta); margin-top: var(--sp-1); }
.item .thumb { width: 56px; height: 56px; border-radius: var(--radius-sm); object-fit: cover; }
.del { opacity: 0; background: transparent; border: 0; color: var(--text-3); font-size: var(--fz-mini); cursor: pointer; transition: opacity 160ms; }
.item:hover .del { opacity: 1; }
.del:hover { color: var(--danger); }
.empty { color: var(--text-3); font-size: var(--fz-meta); padding: var(--sp-5) 0; text-align: center; }
</style>
```

- [ ] **步骤 4：测试 + 构建 + Commit**

```bash
git add frontend/src/components/CommentForm.vue frontend/src/components/CommentList.vue
git commit -m "style(comments): token-driven calm spacing"
```

---

### 任务 9：PostForm + PostEdit 色 token 化

**文件：** 修改 `frontend/src/components/PostForm.vue`、`frontend/src/components/PostEdit.vue`

- [ ] **步骤 1：grep 测试**

运行：`grep -n "data-testid\|class=" frontend/tests/PostForm.test.js frontend/tests/PostEdit.test.js`

- [ ] **步骤 2：替换 PostForm 中的硬编码色**

将所有 `#2563eb` `#94a3b8` `#cbd5e1` 等替换为：

| 旧值 | 新值 |
|---|---|
| `#2563eb` | `var(--accent)` |
| `#94a3b8`、`#cbd5e1` | `var(--border-strong)` |
| `#475569`、`#64748b` | `var(--text-3)` |
| `#dc2626` | `var(--danger)` |
| `#1f2937`、`#0f172a` | `var(--text-1)` |

PostEdit 同处理。其余结构不动。

- [ ] **步骤 3：测试 + 构建 + Commit**

```bash
git add frontend/src/components/PostForm.vue frontend/src/components/PostEdit.vue
git commit -m "style(forms): replace literal colors with tokens"
```

---

### 任务 10：5 维自评 + 文档收尾

**文件：** 修改 `docs/superpowers/specs/2026-06-13-open-design-visual-refresh.md`、`AGENT_LOG.md`、`README.md`

- [ ] **步骤 1：填 5 维自评表**

打开 SPEC §11，按 1–5 分填写列表页 / 详情页两栏；任何 < 3 的条目立刻整改并回到对应任务补丁。

- [ ] **步骤 2：AGENT_LOG**

追加 `2026-06-13 视觉重构（T1–T10）` 段，列每个 commit 的目的；并写下偏离声明：
"采用 Open Design 方法论（DESIGN.md + 5 维 + P0/P1/P2），但本会话内未运行 Open Design daemon/CLI/MCP；未生成 OD 原型/HyperFrame，仅手工把规范落到 Vue 组件。"

- [ ] **步骤 3：README**

在"功能"段最后加一行"前端遵循 [DESIGN.md](DESIGN.md) 品牌契约（受 Open Design 方法论启发）"。

- [ ] **步骤 4：全量验证**

```
cd backend  && .\.venv\Scripts\python.exe -m pytest -q       # 期望 60 passed
cd frontend && npm test --silent                              # 期望 38 passed
cd frontend && npm run build --silent                         # 期望成功
docker compose build                                          # 期望成功
```

- [ ] **步骤 5：Commit**

```bash
git add docs/superpowers/specs/2026-06-13-open-design-visual-refresh.md AGENT_LOG.md README.md
git commit -m "docs: fill self-eval and record visual refresh"
```

---

## 依赖关系

- T1 必须最先完成（其他任务依赖 token 已注入 main.js）。
- T2–T9 之间可并行，但建议顺序执行以减少冲突；如要并行，在 worktree 中按页面切片即可。
- T10 必须最后（依赖 T1–T9 全部完成才能填评估表）。
