# 帖子展示与过滤功能实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 将地点改为校区选择项，并为「南哪寻宝」首页增加寻物 / 寻主帖子展示与三项过滤器。

**架构：** 后端新增 `GET /api/posts`，在数据库查询层按 `post_type`、`category`、`location`、`time_range` 过滤并只返回卡片所需字段。前端将首页从单一发帖入口改为列表页，顶部过滤器控制查询，底部导航切换寻物 / 寻主，发帖流程复用现有 TypePicker 和 PostForm。

**技术栈：** Python 3.11、FastAPI、SQLAlchemy、Pydantic、pytest、Vue 3、Vite、Vitest、axios、SQLite。

---

## 文件结构

### 后端

- 修改：`backend/app/schemas.py`
  - 新增 `CampusLocation`、`TimeRange` 枚举。
  - 将 `PostCreate.location` 从自由文本改为 `CampusLocation`。
  - 新增 `PostListItem` 响应模型。
- 修改：`backend/app/models.py`
  - 为 `posts.location` 增加校区枚举 CHECK 约束。
- 修改：`backend/app/routers/posts.py`
  - `POST /api/posts` 使用校区枚举。
  - 新增 `GET /api/posts`，支持过滤、分页和列表字段裁剪。
- 修改：`backend/tests/test_posts_success.py`
  - 更新现有成功用例中的地点值。
  - 新增校区地点成功用例。
- 修改：`backend/tests/test_posts_validation.py`
  - 更新 schema 测试中的地点值。
  - 新增自由文本地点拒绝测试。
- 创建：`backend/tests/test_posts_list.py`
  - 覆盖列表查询、过滤、字段裁剪和分页上限。

### 前端

- 修改：`frontend/src/api.js`
  - 新增 `listPosts(filters)`。
  - 新增 `imageUrl(path)`。
- 修改：`frontend/src/components/PostForm.vue`
  - 地点输入改为校区 select。
  - 寻主帖联系描述文案改为「联系方式具体描述 *」。
- 创建：`frontend/src/components/PostFilters.vue`
  - 顶部三项过滤器。
- 创建：`frontend/src/components/PostCard.vue`
  - 帖子卡片。
- 创建：`frontend/src/components/PostList.vue`
  - loading、error、empty 和列表渲染。
- 修改：`frontend/src/App.vue`
  - 首页改为列表 + 过滤器 + 底部导航 + 发帖入口。
- 修改：`frontend/tests/PostForm.test.js`
  - 更新地点 select 与文案测试。
- 创建：`frontend/tests/PostFilters.test.js`
- 创建：`frontend/tests/PostCard.test.js`
- 创建：`frontend/tests/App.test.js`

---

## 任务 1：后端地点枚举与 schema 校验

**文件：**
- 修改：`backend/app/schemas.py`
- 修改：`backend/tests/test_posts_validation.py`

- [ ] **步骤 1：编写失败测试**

在 `backend/tests/test_posts_validation.py` 中将 `_payload()` 的默认地点改为 `gulou`，并新增：

```python
def test_invalid_location_rejected():
    from app.schemas import PostCreate
    with pytest.raises(ValidationError):
        PostCreate(**_payload(location="逸夫楼 B201"))
```

同时确认现有测试中所有合法 payload 的 `location` 都使用 `gulou` / `xianlin` / `suzhou` / `pukou`。

- [ ] **步骤 2：运行测试验证失败**

运行：

```powershell
cd backend
pytest tests/test_posts_validation.py -v
```

预期：`test_invalid_location_rejected` 失败，因为当前 `location` 仍接受任意字符串。

- [ ] **步骤 3：实现最少 schema 改动**

在 `backend/app/schemas.py` 中新增枚举并替换 `PostCreate.location`、`PostOut.location` 类型：

```python
class CampusLocation(str, Enum):
    gulou = "gulou"
    xianlin = "xianlin"
    suzhou = "suzhou"
    pukou = "pukou"
```

将：

```python
location: str = Field(..., min_length=1, max_length=100)
```

改为：

```python
location: CampusLocation
```

将 `PostOut.location` 从 `str` 改为：

```python
location: CampusLocation
```

- [ ] **步骤 4：运行测试验证通过**

运行：

```powershell
cd backend
pytest tests/test_posts_validation.py -v
```

预期：全部 PASS。

- [ ] **步骤 5：Commit**

```powershell
git add backend/app/schemas.py backend/tests/test_posts_validation.py
git commit -m "feat: restrict post location to campus enum"
```

---

## 任务 2：后端模型约束与创建接口地点更新

**文件：**
- 修改：`backend/app/models.py`
- 修改：`backend/app/routers/posts.py`
- 修改：`backend/tests/test_posts_success.py`

- [ ] **步骤 1：编写失败测试**

在 `backend/tests/test_posts_success.py` 中把 `_form()` 默认地点改为：

```python
"location": "gulou",
```

新增测试：

```python
def test_create_post_rejects_free_text_location(client):
    r = client.post("/api/posts", data=_form(location="逸夫楼 B201"))
    assert r.status_code == 400
    assert "location" in r.json()["detail"]


def test_create_post_accepts_campus_location(client):
    r = client.post("/api/posts", data=_form(location="xianlin"))
    assert r.status_code == 201, r.text
    assert r.json()["location"] == "xianlin"
```

- [ ] **步骤 2：运行测试验证失败**

运行：

```powershell
cd backend
pytest tests/test_posts_success.py -v
```

预期：至少 `test_create_post_rejects_free_text_location` 在模型约束未更新时失败或行为不完整。

- [ ] **步骤 3：实现模型和创建接口改动**

在 `backend/app/models.py` 的 `__table_args__` 中新增：

```python
CheckConstraint(
    "location IN ('gulou','xianlin','suzhou','pukou')",
    name="ck_location",
),
```

在 `backend/app/routers/posts.py` 创建 `models.Post` 时，将：

```python
location=payload.location,
```

改为：

```python
location=payload.location.value,
```

- [ ] **步骤 4：运行测试验证通过**

运行：

```powershell
cd backend
pytest tests/test_posts_success.py tests/test_posts_validation.py -v
```

预期：全部 PASS。

- [ ] **步骤 5：Commit**

```powershell
git add backend/app/models.py backend/app/routers/posts.py backend/tests/test_posts_success.py
git commit -m "feat: validate campus location on post creation"
```

---

## 任务 3：后端列表 API 与过滤

**文件：**
- 修改：`backend/app/schemas.py`
- 修改：`backend/app/routers/posts.py`
- 创建：`backend/tests/test_posts_list.py`

- [ ] **步骤 1：编写失败测试**

创建 `backend/tests/test_posts_list.py`：

```python
from datetime import datetime, timedelta


def _form(**overrides):
    base = {
        "post_type": "lost",
        "title": "黑色耳机",
        "category": "electronics",
        "description": "降噪耳机",
        "location": "xianlin",
        "event_time": (datetime.now() - timedelta(hours=2)).isoformat(timespec="minutes"),
        "contact_type": "owner_contact",
        "contact_detail": "微信 abc123",
    }
    base.update(overrides)
    return base


def _create(client, **overrides):
    r = client.post("/api/posts", data=_form(**overrides))
    assert r.status_code == 201, r.text
    return r.json()


def test_list_posts_requires_post_type(client):
    r = client.get("/api/posts")
    assert r.status_code == 422


def test_list_posts_filters_by_post_type(client):
    _create(client, post_type="lost", contact_type="owner_contact", title="寻物耳机")
    _create(client, post_type="found", contact_type="self_pickup", title="寻主雨伞")
    r = client.get("/api/posts", params={"post_type": "lost"})
    assert r.status_code == 200, r.text
    titles = [p["title"] for p in r.json()]
    assert titles == ["寻物耳机"]


def test_list_posts_filters_by_category(client):
    _create(client, title="耳机", category="electronics")
    _create(client, title="校园卡", category="id_card")
    r = client.get("/api/posts", params={"post_type": "lost", "category": "id_card"})
    assert [p["title"] for p in r.json()] == ["校园卡"]


def test_list_posts_filters_by_location(client):
    _create(client, title="仙林耳机", location="xianlin")
    _create(client, title="鼓楼耳机", location="gulou")
    r = client.get("/api/posts", params={"post_type": "lost", "location": "gulou"})
    assert [p["title"] for p in r.json()] == ["鼓楼耳机"]


def test_list_posts_filters_by_time_range(client):
    _create(client, title="近期", event_time=(datetime.now() - timedelta(hours=3)).isoformat(timespec="minutes"))
    _create(client, title="较早", event_time=(datetime.now() - timedelta(days=8)).isoformat(timespec="minutes"))
    r = client.get("/api/posts", params={"post_type": "lost", "time_range": "older_than_7d"})
    assert [p["title"] for p in r.json()] == ["较早"]


def test_list_posts_excludes_contact_detail(client):
    _create(client)
    r = client.get("/api/posts", params={"post_type": "lost"})
    body = r.json()[0]
    assert "contact_detail" not in body
    assert "contact_type" not in body
    assert "description" not in body


def test_list_posts_limit_max_100(client):
    r = client.get("/api/posts", params={"post_type": "lost", "limit": 101})
    assert r.status_code == 422
```

- [ ] **步骤 2：运行测试验证失败**

运行：

```powershell
cd backend
pytest tests/test_posts_list.py -v
```

预期：多数用例 FAIL，因为 `GET /api/posts` 尚未实现。

- [ ] **步骤 3：实现响应模型和时间枚举**

在 `backend/app/schemas.py` 新增：

```python
class TimeRange(str, Enum):
    within_1d = "within_1d"
    within_3d = "within_3d"
    within_7d = "within_7d"
    older_than_7d = "older_than_7d"


class PostListItem(BaseModel):
    id: int
    post_type: PostType
    title: str
    category: Category
    image_path: Optional[str]
    location: CampusLocation
    event_time: datetime
    created_at: datetime

    model_config = {"from_attributes": True}
```

- [ ] **步骤 4：实现 GET /api/posts**

在 `backend/app/routers/posts.py` 修改 import：

```python
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from app.schemas import Category, CampusLocation, PostCreate, PostListItem, PostOut, PostType, TimeRange
```

新增路由，放在 `create_post` 前或后均可：

```python
@router.get("/posts", response_model=List[PostListItem])
def list_posts(
    post_type: PostType = Query(...),
    category: Optional[Category] = Query(None),
    location: Optional[CampusLocation] = Query(None),
    time_range: Optional[TimeRange] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(models.Post).filter(models.Post.post_type == post_type.value)

    if category is not None:
        query = query.filter(models.Post.category == category.value)
    if location is not None:
        query = query.filter(models.Post.location == location.value)
    if time_range is not None:
        now = datetime.now()
        if time_range == TimeRange.within_1d:
            query = query.filter(models.Post.event_time >= now - timedelta(days=1))
        elif time_range == TimeRange.within_3d:
            query = query.filter(models.Post.event_time >= now - timedelta(days=3))
        elif time_range == TimeRange.within_7d:
            query = query.filter(models.Post.event_time >= now - timedelta(days=7))
        elif time_range == TimeRange.older_than_7d:
            query = query.filter(models.Post.event_time < now - timedelta(days=7))

    return query.order_by(models.Post.created_at.desc()).offset(offset).limit(limit).all()
```

- [ ] **步骤 5：运行测试验证通过**

运行：

```powershell
cd backend
pytest tests/test_posts_list.py -v
```

预期：全部 PASS。

- [ ] **步骤 6：运行后端全量测试**

运行：

```powershell
cd backend
pytest -v
```

预期：全部 PASS。

- [ ] **步骤 7：Commit**

```powershell
git add backend/app/schemas.py backend/app/routers/posts.py backend/tests/test_posts_list.py
git commit -m "feat: add filtered post listing api"
```

---

## 任务 4：前端 API 封装与发帖表单更新

**文件：**
- 修改：`frontend/src/api.js`
- 修改：`frontend/src/components/PostForm.vue`
- 修改：`frontend/tests/PostForm.test.js`

- [ ] **步骤 1：编写失败测试**

在 `frontend/tests/PostForm.test.js` 中新增：

```javascript
it('地点字段是校区 select', () => {
  const w = mount(PostForm, { props: { postType: 'lost' } })
  const location = w.get('[data-testid="location"]')
  expect(location.element.tagName).toBe('SELECT')
  expect(location.text()).toContain('鼓楼校区')
  expect(location.text()).toContain('仙林校区')
  expect(location.text()).toContain('苏州校区')
  expect(location.text()).toContain('浦口校区')
})

it('found 类型联系方式描述 label 更明确', () => {
  const w = mount(PostForm, { props: { postType: 'found' } })
  expect(w.text()).toContain('联系方式具体描述 *')
})
```

将原有「补齐字段后 emit」测试中的地点值从 `B201` 改为：

```javascript
await w.get('[data-testid="location"]').setValue('gulou')
```

- [ ] **步骤 2：运行测试验证失败**

运行：

```powershell
cd frontend
npm test -- PostForm.test.js
```

预期：地点 select 和新 label 测试 FAIL。

- [ ] **步骤 3：更新 api.js**

在 `frontend/src/api.js` 追加：

```javascript
export async function listPosts(filters) {
  const params = Object.fromEntries(
    Object.entries(filters).filter(([, v]) => v !== '' && v !== null && v !== undefined)
  )
  const r = await http.get('/api/posts', { params })
  return r.data
}

export function imageUrl(path) {
  if (!path) return ''
  if (import.meta.env.PROD) return `${baseURL}/${path}`
  return `/${path}`
}
```

- [ ] **步骤 4：更新 PostForm.vue**

在 `frontend/src/components/PostForm.vue` 中新增：

```javascript
const LOCATIONS = [
  ['gulou', '鼓楼校区'],
  ['xianlin', '仙林校区'],
  ['suzhou', '苏州校区'],
  ['pukou', '浦口校区']
]
```

将地点输入：

```vue
<input data-testid="location" v-model="location" maxlength="100" />
```

替换为：

```vue
<select data-testid="location" v-model="location">
  <option value="" disabled>请选择</option>
  <option v-for="[v, t] in LOCATIONS" :key="v" :value="v">{{ t }}</option>
</select>
```

将 label 表达式：

```vue
{{ postType === 'lost' ? '联系方式 *' : '具体描述 *' }}
```

替换为：

```vue
{{ postType === 'lost' ? '联系方式 *' : '联系方式具体描述 *' }}
```

- [ ] **步骤 5：运行测试验证通过**

运行：

```powershell
cd frontend
npm test -- PostForm.test.js
```

预期：全部 PASS。

- [ ] **步骤 6：Commit**

```powershell
git add frontend/src/api.js frontend/src/components/PostForm.vue frontend/tests/PostForm.test.js
git commit -m "feat: update post form campus location fields"
```

---

## 任务 5：前端过滤器和帖子卡片组件

**文件：**
- 创建：`frontend/src/components/PostFilters.vue`
- 创建：`frontend/src/components/PostCard.vue`
- 创建：`frontend/src/components/PostList.vue`
- 创建：`frontend/tests/PostFilters.test.js`
- 创建：`frontend/tests/PostCard.test.js`

- [ ] **步骤 1：编写 PostFilters 失败测试**

创建 `frontend/tests/PostFilters.test.js`：

```javascript
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import PostFilters from '../src/components/PostFilters.vue'

describe('PostFilters', () => {
  it('三个过滤器默认显示全部', () => {
    const w = mount(PostFilters, {
      props: { filters: { category: '', time_range: '', location: '' } }
    })
    expect(w.get('[data-testid="filter-category"]').element.value).toBe('')
    expect(w.get('[data-testid="filter-time"]').element.value).toBe('')
    expect(w.get('[data-testid="filter-location"]').element.value).toBe('')
    expect(w.text()).toContain('全部种类')
    expect(w.text()).toContain('全部时间')
    expect(w.text()).toContain('全部校区')
  })

  it('修改过滤器时发出 update:filters', async () => {
    const w = mount(PostFilters, {
      props: { filters: { category: '', time_range: '', location: '' } }
    })
    await w.get('[data-testid="filter-location"]').setValue('gulou')
    expect(w.emitted('update:filters')[0][0]).toEqual({
      category: '',
      time_range: '',
      location: 'gulou'
    })
  })
})
```

- [ ] **步骤 2：编写 PostCard 失败测试**

创建 `frontend/tests/PostCard.test.js`：

```javascript
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import PostCard from '../src/components/PostCard.vue'

describe('PostCard', () => {
  const post = {
    id: 1,
    title: '黑色耳机',
    location: 'xianlin',
    event_time: '2026-06-13T15:30:00',
    image_path: 'uploads/2026/06/13/a.png',
    contact_detail: '微信 abc123'
  }

  it('只展示标题、校区、时间和图片', () => {
    const w = mount(PostCard, { props: { post } })
    expect(w.text()).toContain('黑色耳机')
    expect(w.text()).toContain('仙林校区')
    expect(w.text()).toContain('2026-06-13 15:30')
    expect(w.find('img').exists()).toBe(true)
    expect(w.text()).not.toContain('微信 abc123')
  })
})
```

- [ ] **步骤 3：运行测试验证失败**

运行：

```powershell
cd frontend
npm test -- PostFilters.test.js PostCard.test.js
```

预期：组件不存在，测试 FAIL。

- [ ] **步骤 4：实现 PostFilters.vue**

创建 `frontend/src/components/PostFilters.vue`：

```vue
<script setup>
const props = defineProps({ filters: { type: Object, required: true } })
const emit = defineEmits(['update:filters'])

const CATEGORIES = [
  ['electronics', '电子产品类'], ['id_card', '个人证件与卡类'], ['bag', '箱包与收纳'],
  ['accessory', '配饰'], ['clothing', '衣物'], ['daily', '日常小件'],
  ['study', '办公与学习'], ['sports', '运动与户外'], ['personal_care', '个人护理与健康']
]
const TIMES = [
  ['within_1d', '一天以内'], ['within_3d', '三天以内'],
  ['within_7d', '七天以内'], ['older_than_7d', '七天以外']
]
const LOCATIONS = [
  ['gulou', '鼓楼校区'], ['xianlin', '仙林校区'], ['suzhou', '苏州校区'], ['pukou', '浦口校区']
]

function update(key, value) {
  emit('update:filters', { ...props.filters, [key]: value })
}
</script>

<template>
  <section class="filters">
    <select data-testid="filter-category" :value="filters.category" @change="update('category', $event.target.value)">
      <option value="">全部种类</option>
      <option v-for="[v, t] in CATEGORIES" :key="v" :value="v">{{ t }}</option>
    </select>
    <select data-testid="filter-time" :value="filters.time_range" @change="update('time_range', $event.target.value)">
      <option value="">全部时间</option>
      <option v-for="[v, t] in TIMES" :key="v" :value="v">{{ t }}</option>
    </select>
    <select data-testid="filter-location" :value="filters.location" @change="update('location', $event.target.value)">
      <option value="">全部校区</option>
      <option v-for="[v, t] in LOCATIONS" :key="v" :value="v">{{ t }}</option>
    </select>
  </section>
</template>

<style scoped>
.filters { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-bottom: 12px; }
.filters select { padding: 8px 10px; border: 1px solid #cbd5e1; border-radius: 8px; }
@media (max-width: 520px) { .filters { grid-template-columns: 1fr; } }
</style>
```

- [ ] **步骤 5：实现 PostCard.vue**

创建 `frontend/src/components/PostCard.vue`：

```vue
<script setup>
import { imageUrl } from '../api.js'
const props = defineProps({ post: { type: Object, required: true } })

const LOCATIONS = { gulou: '鼓楼校区', xianlin: '仙林校区', suzhou: '苏州校区', pukou: '浦口校区' }
function formatTime(value) {
  return String(value).slice(0, 16).replace('T', ' ')
}
</script>

<template>
  <article class="card">
    <img v-if="post.image_path" :src="imageUrl(post.image_path)" alt="物品图片" class="thumb" />
    <div class="content">
      <h3>{{ post.title }}</h3>
      <p>{{ LOCATIONS[post.location] || post.location }}</p>
      <p>{{ formatTime(post.event_time) }}</p>
    </div>
  </article>
</template>

<style scoped>
.card { display: flex; gap: 12px; padding: 12px; border: 1px solid #e2e8f0; border-radius: 12px; background: white; }
.thumb { width: 72px; height: 72px; object-fit: cover; border-radius: 8px; background: #f1f5f9; }
.content { min-width: 0; }
h3 { margin: 0 0 8px; font-size: 16px; color: #0f172a; }
p { margin: 4px 0; color: #64748b; font-size: 14px; }
</style>
```

- [ ] **步骤 6：实现 PostList.vue**

创建 `frontend/src/components/PostList.vue`：

```vue
<script setup>
import PostCard from './PostCard.vue'
defineProps({
  posts: { type: Array, required: true },
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' },
  postType: { type: String, required: true }
})
</script>

<template>
  <section class="list">
    <p v-if="loading" class="state">加载中...</p>
    <p v-else-if="error" class="state error">{{ error }}</p>
    <p v-else-if="posts.length === 0" class="state">{{ postType === 'lost' ? '暂无寻物帖' : '暂无寻主帖' }}</p>
    <PostCard v-else v-for="post in posts" :key="post.id" :post="post" />
  </section>
</template>

<style scoped>
.list { display: flex; flex-direction: column; gap: 10px; padding-bottom: 88px; }
.state { text-align: center; color: #64748b; padding: 32px 0; }
.error { color: #dc2626; }
</style>
```

- [ ] **步骤 7：运行测试验证通过**

运行：

```powershell
cd frontend
npm test -- PostFilters.test.js PostCard.test.js
```

预期：全部 PASS。

- [ ] **步骤 8：Commit**

```powershell
git add frontend/src/components/PostFilters.vue frontend/src/components/PostCard.vue frontend/src/components/PostList.vue frontend/tests/PostFilters.test.js frontend/tests/PostCard.test.js
git commit -m "feat: add post filters and cards"
```

---

## 任务 6：首页集成列表、过滤器和底部导航

**文件：**
- 修改：`frontend/src/App.vue`
- 创建：`frontend/tests/App.test.js`

- [ ] **步骤 1：编写失败测试**

创建 `frontend/tests/App.test.js`：

```javascript
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import App from '../src/App.vue'
import * as api from '../src/api.js'

vi.mock('../src/api.js', () => ({
  createPost: vi.fn(),
  listPosts: vi.fn(),
  imageUrl: vi.fn(path => `/${path}`)
}))

describe('App', () => {
  beforeEach(() => {
    api.listPosts.mockResolvedValue([])
    api.createPost.mockResolvedValue({ id: 1, post_type: 'lost' })
  })

  it('默认请求寻物列表', async () => {
    mount(App)
    await flushPromises()
    expect(api.listPosts).toHaveBeenCalledWith({ post_type: 'lost', category: '', time_range: '', location: '' })
  })

  it('切换底部导航后请求寻主列表', async () => {
    const w = mount(App)
    await flushPromises()
    await w.get('[data-testid="tab-found"]').trigger('click')
    await flushPromises()
    expect(api.listPosts).toHaveBeenLastCalledWith({ post_type: 'found', category: '', time_range: '', location: '' })
  })
})
```

- [ ] **步骤 2：运行测试验证失败**

运行：

```powershell
cd frontend
npm test -- App.test.js
```

预期：FAIL，因为 App 尚未集成 `listPosts` 和底部导航。

- [ ] **步骤 3：实现 App.vue**

将 `frontend/src/App.vue` 调整为：

```vue
<script setup>
import { onMounted, ref, watch } from 'vue'
import TypePicker from './components/TypePicker.vue'
import PostForm from './components/PostForm.vue'
import PostFilters from './components/PostFilters.vue'
import PostList from './components/PostList.vue'
import { createPost, listPosts } from './api.js'

const view = ref('home')
const activeTab = ref('lost')
const postType = ref(null)
const submitting = ref(false)
const posts = ref([])
const loading = ref(false)
const error = ref('')
const filters = ref({ category: '', time_range: '', location: '' })

function openPicker() { view.value = 'picker' }
function pickType(t) { postType.value = t; view.value = 'form' }
function backHome() { view.value = 'home'; postType.value = null }

async function loadPosts() {
  loading.value = true
  error.value = ''
  try {
    posts.value = await listPosts({ post_type: activeTab.value, ...filters.value })
  } catch (e) {
    error.value = e?.response?.data?.detail || '加载帖子失败'
  } finally {
    loading.value = false
  }
}

function switchTab(tab) {
  activeTab.value = tab
}

async function onSubmit(payload) {
  submitting.value = true
  try {
    const created = await createPost(payload)
    alert('发布成功')
    activeTab.value = created.post_type
    backHome()
    await loadPosts()
  } catch (e) {
    const detail = e?.response?.data?.detail || '提交失败，请稍后重试'
    alert(detail)
  } finally {
    submitting.value = false
  }
}

onMounted(loadPosts)
watch([activeTab, filters], loadPosts, { deep: true })
</script>

<template>
  <main class="page">
    <header class="title">南哪寻宝</header>

    <section v-if="view === 'home'" class="home-list">
      <PostFilters :filters="filters" @update:filters="filters = $event" />
      <PostList :posts="posts" :loading="loading" :error="error" :post-type="activeTab" />
      <button class="primary floating" data-testid="btn-create" @click="openPicker">发帖</button>
      <nav class="bottom-nav">
        <button data-testid="tab-lost" :class="{ active: activeTab === 'lost' }" @click="switchTab('lost')">寻物</button>
        <button data-testid="tab-found" :class="{ active: activeTab === 'found' }" @click="switchTab('found')">寻主</button>
      </nav>
    </section>

    <TypePicker v-else-if="view === 'picker'" @pick="pickType" @cancel="backHome" />

    <PostForm v-else :post-type="postType" @submit="onSubmit" @cancel="backHome" />
  </main>
</template>

<style>
:root { font-family: system-ui, -apple-system, "PingFang SC", sans-serif; background: #f8fafc; }
.page { max-width: 640px; margin: 0 auto; padding: 24px 16px 96px; }
.title { font-size: 24px; font-weight: 700; color: #0f172a; margin-bottom: 16px; }
.home-list { min-height: 70vh; }
.primary { background: #2563eb; color: white; border: 0; padding: 12px 20px; border-radius: 8px; font-size: 16px; cursor: pointer; }
.primary:hover { background: #1d4ed8; }
.floating { position: fixed; right: max(16px, calc((100vw - 640px) / 2 + 16px)); bottom: 72px; box-shadow: 0 8px 20px rgb(37 99 235 / 25%); }
.bottom-nav { position: fixed; left: 50%; bottom: 0; transform: translateX(-50%); width: min(100%, 640px); display: grid; grid-template-columns: 1fr 1fr; background: white; border-top: 1px solid #e2e8f0; }
.bottom-nav button { padding: 14px 0; border: 0; background: transparent; color: #64748b; font-size: 15px; cursor: pointer; }
.bottom-nav button.active { color: #2563eb; font-weight: 700; }
</style>
```

- [ ] **步骤 4：运行测试验证通过**

运行：

```powershell
cd frontend
npm test -- App.test.js
```

预期：全部 PASS。

- [ ] **步骤 5：运行前端全量测试**

运行：

```powershell
cd frontend
npm test
```

预期：全部 PASS。

- [ ] **步骤 6：Commit**

```powershell
git add frontend/src/App.vue frontend/tests/App.test.js
git commit -m "feat: show filtered posts on homepage"
```

---

## 任务 7：文档、全量验证与收尾

**文件：**
- 修改：`README.md`
- 修改：`AGENT_LOG.md`
- 修改：`docs/superpowers/plans/2026-06-13-post-listing-filters-plan.md`

- [ ] **步骤 1：更新 README**

在 `README.md` 的功能说明中加入：

```markdown
- 首页默认展示「寻物」帖子，可通过底部导航切换到「寻主」。
- 支持按物品种类、时间范围和校区过滤帖子。
- 发帖地点固定为鼓楼校区、仙林校区、苏州校区、浦口校区。
```

如果 README 中有发帖字段说明，将地点说明改为：

```markdown
- 丢失 / 捡到地点：必选，鼓楼校区 / 仙林校区 / 苏州校区 / 浦口校区。
```

- [ ] **步骤 2：更新 AGENT_LOG**

在 `AGENT_LOG.md` 追加本轮记录：

```markdown
## 2026-06-13 · 帖子展示与过滤迭代

- **触发技能**：brainstorming、writing-plans、test-driven-development、verification-before-completion。
- **关键需求**：地点枚举化；寻主帖文案调整；首页增加寻物 / 寻主底部导航；顶部增加物品种类、时间、校区过滤器。
- **人工决策**：卡片只展示标题、校区地点、丢失 / 捡到时间和缩略图；本轮不做详情页，不展示联系方式。
- **偏离说明**：如当前 Trae 环境仍无法派发真实 subagent，则继续采用主会话内联执行 + 自评审，并如实记录。
```

- [ ] **步骤 3：勾选 PLAN 任务状态**

在本计划中将已完成任务的复选框从 `- [ ]` 改为 `- [x]`，并在每个任务标题下方补充对应 commit hash。

- [ ] **步骤 4：运行后端全量测试**

运行：

```powershell
cd backend
pytest -v
```

预期：全部 PASS。

- [ ] **步骤 5：运行前端全量测试**

运行：

```powershell
cd frontend
npm test
```

预期：全部 PASS。

- [ ] **步骤 6：运行一键测试**

运行：

```powershell
make test
```

预期：后端和前端测试全部 PASS。

- [ ] **步骤 7：验证 Docker 构建**

运行：

```powershell
docker compose build
```

预期：backend 和 frontend 镜像均构建成功。

- [ ] **步骤 8：Commit**

```powershell
git add README.md AGENT_LOG.md docs/superpowers/plans/2026-06-13-post-listing-filters-plan.md
git commit -m "docs: record post listing implementation workflow"
```

---

## 依赖与并行性

- 任务 1 → 任务 2 → 任务 3 必须串行，后端枚举和模型约束是列表 API 的基础。
- 任务 4 可在任务 1 后开始，但最好等任务 2 确认地点枚举后执行。
- 任务 5 可与任务 3 并行，因为它只依赖 API 契约。
- 任务 6 依赖任务 4 和任务 5。
- 任务 7 依赖所有任务完成。

## 自检

- **规格覆盖度**：本计划覆盖地点枚举化、寻主帖 label 修改、列表 API、顶部过滤器、底部导航、卡片字段限制、发帖成功刷新、测试和验收。
- **占位符扫描**：无「待定」「TODO」「后续实现」等占位内容。
- **类型一致性**：`CampusLocation`、`TimeRange`、`PostListItem`、`listPosts`、`imageUrl` 名称在任务间保持一致。
- **范围控制**：未加入详情页、搜索、分页 UI、联系方式展示或登录功能。
