# DESIGN.md — 南大失物招领品牌契约

> 受 [Open Design](https://github.com/nexu-io/open-design) 方法论启发的离线版设计系统。  
> 本文件是 `frontend/src/styles/tokens.css` 的人类可读对照，所有改动须先在此处描述、再落到 token、再用于组件。

## 设计意图

- **调性**：Notion 风。暖灰底色 + 大留白 + 阅读优先。克制度高于装饰性。
- **核心信念**：让信息（标题、地点、时间、联系方式）说话，UI 退到背景里。
- **首要场景**：校园学生 / 教职工 5 秒内决定"这条帖子值不值得我点开"。

## 色彩

### 中性色（暖灰）

| Token | 值 | 用途 |
|---|---|---|
| `--bg` | `#FAF9F7` | 全局底色 |
| `--surface` | `#FFFFFF` | 卡片、容器、输入背景 |
| `--surface-2` | `#F3F1EC` | 次级容器（筛选栏底、评论框底、折叠提示底） |
| `--border` | `#E8E4DD` | 1px 极细分隔线 |
| `--border-strong` | `#D6D1C7` | 输入框、按钮描边 |
| `--text-1` | `#1F1B16` | 主要文字、标题 |
| `--text-2` | `#4A453E` | 正文 |
| `--text-3` | `#857F76` | 元信息、placeholder、未点击图标 |

不使用 `#000` 与 `#FFF`，避免 AI-slop 默认黑白对比。

### 功能色

| Token | 值 | 用途 |
|---|---|---|
| `--accent` | `#6B5BD2` | 主操作（"我要发帖"、点赞高亮、focus 环） |
| `--accent-hover` | `#5A4BC2` | hover 态 |
| `--danger` | `#C2410C` | 删除按钮 hover、错误提示 |
| `--warning` | `#B45309` | 待处理提示（暂未使用） |
| `--success` | `#15803D` | 成功提示 |

### 语义标签色

| Token | 文字 | 底色 | 用途 |
|---|---|---|---|
| `--lost-tag-fg` | `#9A3412` | `--lost-tag-bg` `#FEF3C7` | "寻物"标签 |
| `--found-tag-fg` | `#166534` | `--found-tag-bg` `#DCFCE7` | "招领"标签 |

## 字体与字号

```
font-family: -apple-system, BlinkMacSystemFont, "PingFang SC",
             "Microsoft YaHei", "Segoe UI", sans-serif;
```

不引入 webfont；依赖操作系统字体栈，规避加载阻塞与字重 FOIT/FOUT。

| Token | px | 行高 | 字重 | 用例 |
|---|---|---|---|---|
| `--fz-display` | 28 | 1.3 | 600 | 详情页帖子标题、首页 Hero 站名 |
| `--fz-h2` | 20 | 1.3 | 600 | "评论"等区块标题 |
| `--fz-body` | 15 | 1.6 | 400 | 列表卡片标题、详情正文 |
| `--fz-meta` | 13 | 1.6 | 400 | 时间、地点、计数、placeholder |
| `--fz-mini` | 12 | 1.4 | 500 | 标签内文字 |

字重只用 400 / 600 两档，禁止 700+ 与 < 400。

## 间距

8pt grid：

| Token | px |
|---|---|
| `--sp-1` | 4 |
| `--sp-2` | 8 |
| `--sp-3` | 12 |
| `--sp-4` | 16 |
| `--sp-5` | 24 |
| `--sp-6` | 32 |
| `--sp-7` | 48 |

不允许出现 5/7/9/13 等台阶外的间距。

## 圆角

| Token | px | 用例 |
|---|---|---|
| `--radius-sm` | 6 | chip、按钮、输入框 |
| `--radius-md` | 10 | 卡片、容器 |
| `--radius-lg` | 14 | 详情页阅读容器 |

## 阴影

| Token | 值 | 用例 |
|---|---|---|
| `--shadow-card` | `0 1px 2px rgba(31,27,22,.04), 0 1px 3px rgba(31,27,22,.06)` | 卡片默认 |
| `--shadow-pop` | `0 4px 16px rgba(31,27,22,.08)` | 卡片 hover、模态 |

## 组件原则

- **按钮**：主操作 `--accent` 实底 + 白字；次操作 `--surface-2` 底 + `--text-1` 字 + `--border-strong` 描边；危险操作默认与次操作同形，hover 才转 `--danger` 文字色。
- **输入框**：`--surface` 底 + `--border-strong` 描边；focus 时 `--accent` 描边 + 1px 同色淡 ring，无 box-shadow 跳变。
- **卡片**：`--surface` 底 + `--shadow-card`；hover `translateY(-2px)` + `--shadow-pop`；transition 160ms ease-out。
- **chip**：高度 28、`--radius-sm`、内边距 4 12，文字 `--fz-meta`，选中态 `--accent` 文字 + `--surface-2` 底。
- **图标**：限内联 SVG / 字符（♥ ←）；不引入 icon 字体。
- **插图**：禁止——避免 AI 生成图片千篇一律；空状态用文字 + 暖灰虚线方框。

## 反 AI-slop 红线

- 不出现 `#000`、`#FFF`、纯灰 `#888`。
- 不出现紫渐变、霓虹高光、玻璃拟态。
- 不出现 emoji 装饰（业务必要除外）。
- 不出现两种以上字体家族。
- 不出现 < 400 字重和 > 600 字重。
- 卡片间距、字号、圆角必须从上述 token 取值。

## 文件落地

- 实际值在 `frontend/src/styles/tokens.css`。本文件以人类阅读为主，token 一旦变化两处一并更新。
- 列表页 / 详情页相关组件作为 P0 全部 token 化。
- 表单页（PostForm / PostEdit / CommentForm）作为 P1 token 化（替换硬编码色，保留版式）。
