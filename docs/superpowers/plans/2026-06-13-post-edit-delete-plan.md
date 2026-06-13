# 帖子编辑与删除 实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 给“南哪寻宝”帖子详情页加上作者本人的编辑与删除入口，作者通过 `X-Anon-Id` 识别，编辑全字段（除 `post_type`）并支持图片替换/移除，删除时级联清理评论、点赞与图片。

**架构：** 后端在 `posts` 表新增 `anon_id` 列；新增 `PUT /api/posts/{id}` 与 `DELETE /api/posts/{id}` 路由；详情接口新增 `mine` 字段。前端在 `PostDetail.vue` 内部维护 `mode` 切换；新增 `PostEdit.vue` 子组件与 `updatePost / deletePost` API；删除走 `confirm` 二次确认 → emit back → App 回首页。

**技术栈：** Python 3.11 + FastAPI + SQLAlchemy + SQLite；Vue 3 + Vite + axios + Vitest。

**SPEC：** [docs/superpowers/specs/2026-06-13-post-edit-delete-design.md](../specs/2026-06-13-post-edit-delete-design.md)

---

## 文件结构

### 新增

- `backend/tests/test_post_edit.py`
- `backend/tests/test_post_delete.py`
- `frontend/src/components/PostEdit.vue`
- `frontend/tests/PostEdit.test.js`
- `frontend/tests/PostDetailEditDelete.test.js`

### 修改

- `backend/app/models.py`：`Post` 增加 `anon_id` 列。
- `backend/app/database.py`：`init_db()` 中确保 `posts.anon_id` 存在。
- `backend/app/schemas.py`：`PostDetailOut` 增加 `mine: bool`。
- `backend/app/routers/posts.py`：`POST` 写入 `anon_id`；`GET /{id}` 算 `mine`；新增 `PUT /{id}` 与 `DELETE /{id}`。
- `backend/tests/test_post_detail.py`：补 `mine` / `anon_id` 用例。
- `frontend/src/api.js`：新增 `updatePost / deletePost`。
- `frontend/src/components/PostDetail.vue`：增加 `mode` 切换、编辑/删除按钮、删除回首页。
- `frontend/src/App.vue`：detail `back` 后刷新 home 列表。
- `README.md`、`AGENT_LOG.md`：记录功能与测试用例数。

---

## 任务 1：后端 `posts.anon_id` 列与 `mine` 字段

**文件：** 修改 `backend/app/models.py`、`backend/app/schemas.py`、`backend/app/database.py`、`backend/app/routers/posts.py`；测试 `backend/tests/test_post_detail.py`。

- [ ] **步骤 1：编写失败的测试** 在 `test_post_detail.py` 末尾追加：

```python
def test_post_has_anon_id_column(client):
    from sqlalchemy import inspect
    from app.database import engine
    cols = {c["name"] for c in inspect(engine).get_columns("posts")}
    assert "anon_id" in cols


def test_post_detail_returns_mine_flag(client):
    pid = _create_post(client)["id"]
    r = client.get(f"/api/posts/{pid}", headers={"X-Anon-Id": ANON})
    assert r.status_code == 200
    body = r.json()
    assert "mine" in body
    assert body["mine"] is False
```

- [ ] **步骤 2：运行测试验证失败** `cd backend; .\.venv\Scripts\python.exe -m pytest tests/test_post_detail.py -v` 预期：2 FAIL。

- [ ] **步骤 3：编写最少实现代码**
  - `models.py` 内 `Post` 末尾新增 `anon_id = Column(String(36), nullable=True)`。
  - `schemas.py`：`PostDetailOut(PostOut)` 加 `mine: bool`。
  - `database.py` 在 `init_db()` 末尾新增 `_ensure_column` 工具：

    ```python
    def _ensure_column(table, column, ddl):
        from sqlalchemy import inspect, text
        insp = inspect(engine)
        if table not in insp.get_table_names():
            return
        cols = {c["name"] for c in insp.get_columns(table)}
        if column in cols:
            return
        with engine.begin() as conn:
            conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {ddl}"))
    ```

    在 `init_db()` 末尾调用 `_ensure_column("posts", "anon_id", "anon_id VARCHAR(36)")`。
  - `posts.py::get_post` 末尾改返回：

    ```python
    mine = post.anon_id is not None and post.anon_id == anon_id
    base = PostOut.model_validate(post).model_dump()
    return PostDetailOut(**base, like_count=like_count, liked_by_me=liked, mine=mine)
    ```

- [ ] **步骤 4：运行测试验证通过** `pytest tests/test_post_detail.py -v` 预期：原 5 + 新 2 = 7 passed。
- [ ] **步骤 5：Commit** `git add backend/app/models.py backend/app/schemas.py backend/app/database.py backend/app/routers/posts.py backend/tests/test_post_detail.py && git commit -m "feat(backend): add post anon_id column and mine flag"`

---

## 任务 2：发帖接口写入 anon_id

**文件：** 修改 `backend/app/routers/posts.py`、`backend/tests/test_post_detail.py`。

- [ ] **步骤 1：编写失败的测试** 在 `test_post_detail.py` 末尾追加：

```python
def test_post_detail_mine_true_for_author(client):
    headers = {"X-Anon-Id": ANON}
    r = client.post("/api/posts", headers=headers, data={
        "post_type": "lost", "title": "黑色雨伞", "category": "daily",
        "description": "长柄", "location": "gulou",
        "event_time": (datetime.now() - timedelta(hours=1)).isoformat(timespec="minutes"),
        "contact_type": "owner_contact", "contact_detail": "微信 abc123",
    })
    pid = r.json()["id"]
    assert client.get(f"/api/posts/{pid}", headers=headers).json()["mine"] is True
    other = {"X-Anon-Id": "22222222-2222-2222-2222-222222222222"}
    assert client.get(f"/api/posts/{pid}", headers=other).json()["mine"] is False
```

- [ ] **步骤 2：运行测试验证失败** `pytest tests/test_post_detail.py::test_post_detail_mine_true_for_author -v` 预期：FAIL。
- [ ] **步骤 3：编写最少实现代码** `posts.py::create_post` 签名末尾添加 `anon_id: str = Depends(get_anon_id)`，并在 `models.Post(...)` 构造时加上 `anon_id=anon_id`。
- [ ] **步骤 4：运行测试验证通过** `pytest tests/test_post_detail.py -v` 预期：8 passed。
- [ ] **步骤 5：Commit** `git add backend/app/routers/posts.py backend/tests/test_post_detail.py && git commit -m "feat(backend): persist post author anon_id"`

---

## 任务 3：后端 PUT /api/posts/{id}

**文件：** 修改 `backend/app/routers/posts.py`；测试 `backend/tests/test_post_edit.py`。

- [ ] **步骤 1：编写失败的测试** 新增 `test_post_edit.py`，覆盖：
  - 全字段更新返回 200，`title/location/contact_detail/mine` 与请求一致。
  - 非作者 PUT 返回 403。
  - 不存在的 id 返回 404。
  - 上传新图片：返回 `image_path` 以 `.png` 结尾。
  - 带初始图片，`remove_image=true` 后 `image_path == null` 且原文件被磁盘清理。
  - PUT 时即使带 `post_type=found`（form 多余字段）也保持 `post_type='lost'`。

  常量、`_create`、`_form` 见 SPEC §3 的字段集，`PNG` 沿用其他测试中的合法 1×1 PNG 字节串。

- [ ] **步骤 2：运行测试验证失败** `pytest tests/test_post_edit.py -v` 预期：6 FAIL。
- [ ] **步骤 3：编写最少实现代码** 在 `posts.py` 末尾追加 `PUT /posts/{post_id}`：
  - 依赖 `get_anon_id`；查 `post`，404/403。
  - `datetime.fromisoformat(event_time)` 失败 → 400。
  - 用 `PostCreate(post_type=post.post_type, title=..., ...)` 复用校验，失败 → 400。
  - 图片处理：上传 → `storage.save_image`；否则 `remove_image in {"true","1","yes"}`（小写）→ 清空；否则保留。
  - 更新字段后 `db.commit() + db.refresh(post)`；commit 失败 → 回滚 + 删除新落盘图片 → 500。
  - 提交后再 `storage.delete_image(old_image_rel)`（仅当 drop 标记为真）。
  - 返回 `PostDetailOut(..., mine=True)`，`like_count / liked_by_me` 用与 `get_post` 相同方式查询。
- [ ] **步骤 4：运行测试验证通过** `pytest tests/test_post_edit.py -v` 预期：6 passed。
- [ ] **步骤 5：Commit** `git add backend/app/routers/posts.py backend/tests/test_post_edit.py && git commit -m "feat(backend): add post update endpoint"`

---

## 任务 4：后端 DELETE /api/posts/{id} 级联

**文件：** 修改 `backend/app/routers/posts.py`；测试 `backend/tests/test_post_delete.py`。

- [ ] **步骤 1：编写失败的测试** 新增 `test_post_delete.py`：
  - `test_delete_post_forbidden_for_other_anon`：B 删 A 的帖子 → 403。
  - `test_delete_post_404`：不存在 → 404。
  - `test_delete_post_cascades`：A 发带图帖；B 点赞；A 发带图评论；DELETE 后：
    - `GET /api/posts/{id}` → 404；
    - `GET /api/posts/{id}/comments` → 404；
    - 主图与评论图磁盘文件均不存在。

- [ ] **步骤 2：运行测试验证失败** `pytest tests/test_post_delete.py -v` 预期：3 FAIL。
- [ ] **步骤 3：编写最少实现代码** 在 `posts.py` 末尾追加：

```python
@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: Session = Depends(get_db),
                anon_id: str = Depends(get_anon_id)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="post not found")
    if post.anon_id is None or post.anon_id != anon_id:
        raise HTTPException(status_code=403, detail="not your post")
    comments = db.query(models.PostComment).filter(models.PostComment.post_id == post_id).all()
    comment_images = [c.image_path for c in comments if c.image_path]
    main_image = post.image_path
    db.query(models.PostComment).filter(models.PostComment.post_id == post_id).delete(synchronize_session=False)
    db.query(models.PostLike).filter(models.PostLike.post_id == post_id).delete(synchronize_session=False)
    db.delete(post)
    db.commit()
    for rel in comment_images:
        storage.delete_image(rel)
    if main_image:
        storage.delete_image(main_image)
    return None
```

- [ ] **步骤 4：运行测试验证通过** `pytest tests/test_post_delete.py -v` 预期：3 passed；并 `pytest -q` 全套绿。
- [ ] **步骤 5：Commit** `git add backend/app/routers/posts.py backend/tests/test_post_delete.py && git commit -m "feat(backend): add post delete endpoint with cascade"`

---

## 任务 5：前端 updatePost / deletePost

**文件：** 修改 `frontend/src/api.js`、`frontend/tests/api.test.js`。

- [ ] **步骤 1：编写失败的测试** 在 `api.test.js` 末尾追加：

```js
import * as api from '../src/api.js'

describe('post update/delete API surface', () => {
  it('暴露 updatePost 与 deletePost', () => {
    expect(typeof api.updatePost).toBe('function')
    expect(typeof api.deletePost).toBe('function')
  })
})
```

- [ ] **步骤 2：运行测试验证失败** `cd frontend; npx vitest run tests/api.test.js` 预期：FAIL。
- [ ] **步骤 3：编写最少实现代码** `api.js` 末尾追加：

```js
export async function updatePost(id, form) {
  const fd = new FormData()
  Object.entries(form).forEach(([k, v]) => {
    if (v === null || v === undefined || v === '') return
    fd.append(k, v)
  })
  const r = await http.put(`/api/posts/${id}`, fd, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return r.data
}

export async function deletePost(id) {
  await http.delete(`/api/posts/${id}`)
}
```

- [ ] **步骤 4：运行测试验证通过** `npx vitest run tests/api.test.js` 预期：原 2 + 新 1 = 3 passed。
- [ ] **步骤 5：Commit** `git add frontend/src/api.js frontend/tests/api.test.js && git commit -m "feat(frontend): add updatePost and deletePost"`

---

## 任务 6：前端 PostEdit 组件

**文件：** 创建 `frontend/src/components/PostEdit.vue`、`frontend/tests/PostEdit.test.js`。

- [ ] **步骤 1：编写失败的测试** `PostEdit.test.js` 含 3 个用例：
  - 表单预填：`[data-testid="edit-title"].value === '黑色雨伞'`，`[data-testid="edit-location"].value === 'gulou'`。
  - 点击保存调用 `updatePost(id, payload)`，`payload.title === '新标题'`，且 emit `saved` 含返回值。
  - 无修改时点击 `[data-testid="edit-cancel"]` 直接 emit `cancel`。

  通过 `vi.mock('../src/api.js', () => ({ updatePost: vi.fn(), imageUrl: p => '/'+p }))` 桩入。

- [ ] **步骤 2：运行测试验证失败** `npx vitest run tests/PostEdit.test.js` 预期：组件不存在 FAIL。
- [ ] **步骤 3：编写最少实现代码** 新增 `PostEdit.vue`：
  - `defineProps({ post })`、`defineEmits(['saved','cancel'])`。
  - `reactive(form)` 用 props 初始化；`event_time` 取前 16 位适配 `<input type="datetime-local">`。
  - 9 类 `CATEGORIES`、4 校区 `LOCATIONS`、依据 `post.post_type` 选择 `CONTACT_TYPES`。
  - `onFile` 校验 jpg/png/webp 与 5MB；`removeImage` 复选框；`newImage` 优先于 `removeImage`。
  - `dirty` computed：任一字段、新图、移除勾选与原值不一致。
  - `onSave` → 组装 payload（含 image / remove_image）→ `updatePost(post.id, payload)` → emit `saved`。
  - `onCancel` → `dirty` 时 `confirm('放弃未保存的修改？')`，否则直接 emit `cancel`。
  - 模板含 `data-testid="edit-title"` `edit-category` `edit-location` `edit-cancel` `edit-save` 等钩子。

- [ ] **步骤 4：运行测试验证通过** `npx vitest run tests/PostEdit.test.js` 预期：3 passed。
- [ ] **步骤 5：Commit** `git add frontend/src/components/PostEdit.vue frontend/tests/PostEdit.test.js && git commit -m "feat(frontend): add post edit form"`

---

## 任务 7：PostDetail 集成编辑/删除按钮与切换

**文件：** 修改 `frontend/src/components/PostDetail.vue`；测试 `frontend/tests/PostDetailEditDelete.test.js`。

- [ ] **步骤 1：编写失败的测试** 新增 `PostDetailEditDelete.test.js` 含 4 个用例：
  - `mine=false`：`[data-testid="post-edit"]` 与 `post-delete` 都不存在。
  - `mine=true`：点击 `post-edit` 后，`findComponent({ name: 'PostEdit' })` 存在。
  - 删除：`window.confirm` mock 返回 `true` → 调用 `deletePost(1)` → emit `back`。
  - 取消：`window.confirm` 返回 `false` → 不调用 `deletePost`。

  `vi.mock('../src/api.js')` 同时桩入既有的 `getPost / toggleLike / listComments / createComment / deleteComment / imageUrl` 与新增的 `updatePost / deletePost`。

- [ ] **步骤 2：运行测试验证失败** `npx vitest run tests/PostDetailEditDelete.test.js` 预期：4 FAIL。
- [ ] **步骤 3：编写最少实现代码** 修改 `PostDetail.vue`：
  - 顶部 import 增 `deletePost / updatePost / PostEdit`。
  - 新增 `const mode = ref('view')`、`onEdit / onCancelEdit / onSaved / onDelete`。`onSaved(updated)` 用返回值替换 `post.value` 并 `mode='view'`。`onDelete` `confirm` 通过后 `await deletePost(props.postId)` → `emit('back')`。
  - 模板 `<header class="bar">` 中追加：

    ```vue
    <div v-if="post && post.mine && mode === 'view'" class="actions">
      <button data-testid="post-edit" class="ghost" @click="onEdit">编辑</button>
      <button data-testid="post-delete" class="danger" @click="onDelete">删除</button>
    </div>
    ```

  - 用 `<template v-if="mode === 'view'">` 包裹原 `<article>` 与评论 `<section>`；增加 `<PostEdit v-else-if="post" :post="post" @saved="onSaved" @cancel="onCancelEdit" />`。
  - CSS 追加 `.actions / .ghost / .danger` 样式。

- [ ] **步骤 4：运行测试验证通过** `npx vitest run tests/PostDetailEditDelete.test.js tests/PostDetail.test.js` 预期：4 + 3 = 7 passed；`npm test --silent` 整体绿。
- [ ] **步骤 5：Commit** `git add frontend/src/components/PostDetail.vue frontend/tests/PostDetailEditDelete.test.js && git commit -m "feat(frontend): wire edit and delete on post detail"`

---

## 任务 8：App 在删除后刷新首页列表

**文件：** 修改 `frontend/src/App.vue`、`frontend/tests/App.test.js`。

- [ ] **步骤 1：编写失败的测试** 在 `App.test.js` 现有 mock 中补 `updatePost: vi.fn()` 与 `deletePost: vi.fn()`，新增用例：

```js
it('帖子详情发出 back 后刷新首页列表', async () => {
  listPosts.mockResolvedValue([
    { id: 5, title: 'x', location: 'gulou', event_time: '2026-06-12T18:30:00', image_path: null }
  ])
  getPost.mockResolvedValue({
    id: 5, post_type: 'lost', title: 'x', category: 'daily',
    image_path: null, description: '', location: 'gulou',
    event_time: '2026-06-12T18:30:00', contact_type: 'owner_contact',
    contact_detail: '...', created_at: '2026-06-13T10:00:00',
    like_count: 0, liked_by_me: false, mine: true
  })
  listComments.mockResolvedValue([])
  const w = mount(App)
  await flushPromises()
  await w.get('[data-testid="post-card"]').trigger('click')
  await flushPromises()
  const before = listPosts.mock.calls.length
  await w.findComponent({ name: 'PostDetail' }).vm.$emit('back')
  await flushPromises()
  expect(listPosts.mock.calls.length).toBeGreaterThan(before)
})
```

- [ ] **步骤 2：运行测试验证失败** `npx vitest run tests/App.test.js` 预期：新用例 FAIL（back 之后 App 没有刷新）。
- [ ] **步骤 3：编写最少实现代码** `App.vue`：
  - `backHome` 之外新增 `onDetailBack`：

    ```js
    async function onDetailBack() {
      backHome()
      await loadPosts()
    }
    ```

  - 模板里把 `<PostDetail @back="backHome" />` 改为 `<PostDetail @back="onDetailBack" />`。
- [ ] **步骤 4：运行测试验证通过** `npx vitest run tests/App.test.js` 预期：原 4 + 新 1 = 5 passed；`npm test --silent` 全套绿。
- [ ] **步骤 5：Commit** `git add frontend/src/App.vue frontend/tests/App.test.js && git commit -m "feat(frontend): refresh home list after detail back"`

---

## 任务 9：文档与全量验证

**文件：** 修改 `README.md`、`AGENT_LOG.md`。

- [ ] **步骤 1：更新文档**
  - README 在“功能”部分增加“详情页支持作者本人编辑/删除自己的帖子（删除会级联清理评论、点赞与图片）”。
  - README 测试用例数：后端 48 → 60、前端 29 → 38。
  - AGENT_LOG 追加“2026-06-13 帖子编辑与删除功能实现”章节，列出 commit、TDD 节奏、最终验证结果。

- [ ] **步骤 2：全量验证**

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest -v

cd ..\frontend
npm test

cd ..\frontend
npm run build

cd ..
docker compose build
```

预期：后端 60 / 前端 38 / 构建成功 / Docker 构建成功。

- [ ] **步骤 3：Commit** `git add README.md AGENT_LOG.md && git commit -m "docs: record post edit and delete"`

---

## 自检

- 规格覆盖度：
  - SPEC §3.1 详情页入口 → 任务 7。
  - SPEC §3.2 编辑态字段、取消、保存、图片处理 → 任务 6 + 任务 7。
  - SPEC §3.3 权限模型（`anon_id` 列、`mine`、403/404）→ 任务 1 + 任务 2 + 任务 3 + 任务 4。
  - SPEC §3.4 删除联动 → 任务 4 + 任务 7。
  - SPEC §6 数据模型变更（含历史 DB `ALTER`）→ 任务 1 的 `_ensure_column`。
  - SPEC §9 验收 1–8 → 任务 7/7/6/3/3/3+4/4/9。
- 占位符扫描：无 TODO；任务 6/7 用结构化要点描述组件骨架，关键代码段直接给出，避免计划过长。
- 类型一致性：`PostDetailOut` 在所有任务里同时含 `like_count / liked_by_me / mine`；`PUT` 与 `GET` 返回结构一致；前端 `updatePost(id, payload)` 与后端 multipart 字段一一对应；`PostEdit.vue` `data-testid` 命名与测试中一致。

---

## 执行交接

计划已完成并保存到 `docs/superpowers/plans/2026-06-13-post-edit-delete-plan.md`。两种执行方式：

1. 子代理驱动（推荐）—— 每任务派发新子代理 + 两阶段审查。
2. 内联执行 —— 用 `executing-plans` 批量执行并设有检查点。

选哪种方式？另外，是否要按 SPEC 流程先创建一个隔离 worktree（如 `feature/post-edit-delete`）再开工？
