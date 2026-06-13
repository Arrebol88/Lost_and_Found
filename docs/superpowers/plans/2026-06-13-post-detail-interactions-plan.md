# 帖子详情页与点赞、评论交互 实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 在“南哪寻宝”现有发帖与列表功能之上，新增帖子详情页、匿名点赞 toggle、评论发布与作者删除功能。

**架构：** FastAPI 端新增 `post_likes`、`post_comments` 两张表，共享 `X-Anon-Id` header 作为弱身份；前端新增 `view='detail'` 视图，点击 `PostCard` 跳转，详情页内联 `PostDetail.vue` 与子组件 `CommentForm.vue`、`CommentList.vue`。

**技术栈：** Python 3.11 + FastAPI + SQLAlchemy + SQLite；Vue 3 + Vite + axios + Vitest；不引入 vue-router。

**SPEC：** [docs/superpowers/specs/2026-06-13-post-detail-interactions-design.md](../specs/2026-06-13-post-detail-interactions-design.md)

---

## 文件结构

### 新增

- `backend/app/routers/comments.py`：评论与帖子互动 API（含 `DELETE /api/comments/{id}`）。
- `backend/tests/test_post_detail.py`、`test_post_likes.py`、`test_post_comments.py`。
- `frontend/src/components/PostDetail.vue`、`CommentForm.vue`、`CommentList.vue`。
- `frontend/tests/PostDetail.test.js`、`CommentForm.test.js`、`CommentList.test.js`、`api.test.js`。

### 修改

- `backend/app/models.py`：新增 `PostLike`、`PostComment`。
- `backend/app/schemas.py`：新增 `PostDetailOut`、`LikeToggleOut`、`CommentOut`。
- `backend/app/main.py`：注册评论 router。
- `backend/app/routers/posts.py`：新增 `GET /api/posts/{id}` 与 `POST /api/posts/{id}/likes`、`get_anon_id` 依赖。
- `frontend/src/api.js`：新增详情/点赞/评论 API，axios 拦截器注入 `X-Anon-Id`。
- `frontend/src/components/PostCard.vue`：整卡可点击。
- `frontend/src/components/PostList.vue`：透传 `select` 事件。
- `frontend/src/App.vue`：新增 `view='detail'`。
- `README.md`、`AGENT_LOG.md`：记录功能与最终测试用例数。

---

## 任务 1：后端表结构与 schema 基线

**文件：** 修改 `backend/app/models.py`、`backend/app/schemas.py`；测试 `backend/tests/test_post_detail.py`。

- [ ] **步骤 1：编写失败的测试** 新增 `test_post_detail.py`，断言 `post_likes` 表存在，含列 `{id, post_id, anon_id, created_at}`，并在 `(post_id, anon_id)` 上有唯一约束；`post_comments` 表存在，含列 `{id, post_id, anon_id, content, image_path, created_at}`。
- [ ] **步骤 2：运行测试验证失败** `cd backend; .\.venv\Scripts\python.exe -m pytest tests/test_post_detail.py -v` 预期：2 FAIL。
- [ ] **步骤 3：编写最少实现代码** `models.py` 新增 `PostLike`、`PostComment` SQLAlchemy 类；`schemas.py` 新增 `PostDetailOut(PostOut)` 加 `like_count: int / liked_by_me: bool`、`LikeToggleOut(BaseModel)` 含 `liked / like_count`、`CommentOut(BaseModel)` 含 `id / post_id / content / image_path / created_at / mine`，`model_config = {"from_attributes": True}`。
- [ ] **步骤 4：运行测试验证通过** `pytest tests/test_post_detail.py -v` 预期：2 passed。
- [ ] **步骤 5：Commit** `git add backend/app/models.py backend/app/schemas.py backend/tests/test_post_detail.py && git commit -m "feat(backend): add likes and comments tables"`

---

## 任务 2：后端帖子详情接口 GET /api/posts/{id}

**文件：** 修改 `backend/app/routers/posts.py`；测试 `backend/tests/test_post_detail.py`。

- [ ] **步骤 1：编写失败的测试** 在 `test_post_detail.py` 追加：
  - `_create_post(client)` 复用现有发帖接口生成一条 `lost` + `owner_contact` + `contact_detail="微信 abc123"` 的帖子。
  - `test_get_post_detail_returns_full_fields`：`GET /api/posts/{pid}` 带合法 `X-Anon-Id`，断言 `status==200`、`contact_detail=="微信 abc123"`、`like_count==0`、`liked_by_me is False`。
  - `test_get_post_detail_404_for_missing`：`GET /api/posts/9999` → 404。
  - `test_get_post_detail_requires_anon_id`：不带 `X-Anon-Id` → 400。
- [ ] **步骤 2：运行测试验证失败** `pytest tests/test_post_detail.py -v` 预期：3 新用例 FAIL。
- [ ] **步骤 3：编写最少实现代码**
  - `posts.py` 顶部追加 `import re` 与 `Header`，并 `from app.schemas import LikeToggleOut, PostDetailOut`。
  - 新增模块级常量 `_UUID_RE = re.compile(r"^[0-9a-fA-F]{8}-...{12}$")`，与依赖：

    ```python
    def get_anon_id(x_anon_id: Optional[str] = Header(None, alias="X-Anon-Id")) -> str:
        if not x_anon_id or not _UUID_RE.match(x_anon_id):
            raise HTTPException(status_code=400, detail="anon_id: 必须是 UUID")
        return x_anon_id
    ```

  - 新增路由 `GET /posts/{post_id}`：查询 `models.Post` 不存在则 404；统计 `PostLike` 数量；判断 `(post_id, anon_id)` 是否点赞；返回 `PostDetailOut(**PostOut.model_validate(post).model_dump(), like_count=..., liked_by_me=...)`。
- [ ] **步骤 4：运行测试验证通过** `pytest tests/test_post_detail.py -v` 预期：5 passed。
- [ ] **步骤 5：Commit** `git add backend/app/routers/posts.py backend/tests/test_post_detail.py && git commit -m "feat(backend): add post detail endpoint"`

---

## 任务 3：后端点赞 toggle 接口

**文件：** 修改 `backend/app/routers/posts.py`；测试 `backend/tests/test_post_likes.py`。

- [ ] **步骤 1：编写失败的测试** 新增 `test_post_likes.py`：
  - 常量 `ANON_A`、`ANON_B` 为合法 UUID。
  - `test_like_requires_anon_id`：不带 header → 400。
  - `test_like_toggles_for_same_anon`：同 anon 连点 3 次依次得 `{liked:True,like_count:1}`、`{liked:False,0}`、`{liked:True,1}`。
  - `test_like_independent_per_anon`：A 点赞后 B 再点赞 → `{liked:True,like_count:2}`。
  - `test_like_post_not_found`：`POST /api/posts/9999/likes` → 404。
- [ ] **步骤 2：运行测试验证失败** `pytest tests/test_post_likes.py -v` 预期：4 FAIL。
- [ ] **步骤 3：编写最少实现代码** 在 `posts.py` 末尾新增：

  ```python
  @router.post("/posts/{post_id}/likes", response_model=LikeToggleOut)
  def toggle_like(post_id: int, db: Session = Depends(get_db),
                  anon_id: str = Depends(get_anon_id)):
      post = db.query(models.Post).filter(models.Post.id == post_id).first()
      if post is None:
          raise HTTPException(status_code=404, detail="post not found")
      existing = db.query(models.PostLike).filter(
          models.PostLike.post_id == post_id, models.PostLike.anon_id == anon_id
      ).first()
      if existing is None:
          db.add(models.PostLike(post_id=post_id, anon_id=anon_id))
          db.commit()
          liked = True
      else:
          db.delete(existing)
          db.commit()
          liked = False
      count = db.query(models.PostLike).filter(models.PostLike.post_id == post_id).count()
      return LikeToggleOut(liked=liked, like_count=count)
  ```

- [ ] **步骤 4：运行测试验证通过** `pytest tests/test_post_likes.py -v` 预期：4 passed。
- [ ] **步骤 5：Commit** `git add backend/app/routers/posts.py backend/tests/test_post_likes.py && git commit -m "feat(backend): add like toggle endpoint"`

---

## 任务 4：后端评论 CRUD 接口

**文件：** 创建 `backend/app/routers/comments.py`；修改 `backend/app/main.py`；测试 `backend/tests/test_post_comments.py`。

- [ ] **步骤 1：编写失败的测试** 新增 `test_post_comments.py`，常量 `ANON_A/B`、`PNG` 字节串。`_create_post` 复用既有发帖。用例：
  - `test_create_comment_text_only`：仅 `content="我也见过"` → 201，`mine=True`，`image_path is None`。
  - `test_create_comment_rejects_empty_content`：`content="  "` → 400。
  - `test_create_comment_with_image`：`files={"image": ("a.png", PNG, "image/png")}` → 201，`image_path` 以 `.png` 结尾。
  - `test_list_comments_sorted_desc_with_mine_flag`：A、B 各发一条，列表按时间倒序，`mine` 正确。
  - `test_delete_comment_only_by_author`：B 删 A 的评论 → 403；A 删 → 204。
  - `test_delete_comment_removes_image_file`：带图评论删除后磁盘文件不存在。
- [ ] **步骤 2：运行测试验证失败** `pytest tests/test_post_comments.py -v` 预期：6 FAIL。
- [ ] **步骤 3：编写最少实现代码**
  - 新建 `comments.py`，`router = APIRouter(prefix="/api", tags=["comments"])`，依赖 `get_anon_id` 复用 `app.routers.posts.get_anon_id`。实现：
    - `GET /posts/{post_id}/comments` → 检查帖子存在、按 `created_at DESC, id DESC` 返回 `List[CommentOut]`，`mine` 由当前 `anon_id` 判断。
    - `POST /posts/{post_id}/comments` (multipart `content` 必填、`image` 可选) → strip 空白后校验 1..200；图片走 `storage.save_image`，复用发帖的图片错误码 (413/400)；DB 写失败回滚并 `storage.delete_image`。
    - `DELETE /comments/{id}` → 不存在 404；`anon_id != row.anon_id` → 403；删除并清理图片，返回 204。
  - 修改 `main.py`：`from app.routers import posts, comments` 并 `app.include_router(comments.router)`。
- [ ] **步骤 4：运行测试验证通过** `pytest tests/test_post_comments.py -v` 预期：6 passed。
- [ ] **步骤 5：Commit** `git add backend/app/routers/comments.py backend/app/main.py backend/tests/test_post_comments.py && git commit -m "feat(backend): add comment crud endpoints"`

---

## 任务 5：前端 axios 注入 anon_id 并新增详情/点赞/评论 API

**文件：** 修改 `frontend/src/api.js`；新增 `frontend/tests/api.test.js`。

- [ ] **步骤 1：编写失败的测试** 新增 `api.test.js`：
  - `beforeEach` 清空 `localStorage`。
  - `首次调用 ensureAnonId 生成并持久化 UUID`：返回值匹配 `/^[0-9a-f-]{36}$/i`，`localStorage.nju_anon_id` 与之相等。
  - `已有则复用`：预置 UUID 后再调用，返回值不变。
- [ ] **步骤 2：运行测试验证失败** `cd frontend; npx vitest run tests/api.test.js` 预期：FAIL，`ensureAnonId is not a function`。
- [ ] **步骤 3：编写最少实现代码** 修改 `api.js`：
  - 导出 `ensureAnonId()`：localStorage 读，缺失则 `crypto.randomUUID()`（兜底正则模板）写入。
  - axios 实例 `http.interceptors.request.use(cfg => { cfg.headers['X-Anon-Id'] = ensureAnonId(); return cfg })`。
  - 新增 `getPost(id)`、`toggleLike(id)`、`listComments(postId)`、`createComment(postId, {content, image})`（multipart）、`deleteComment(id)`；保留 `createPost / listPosts / imageUrl`。
- [ ] **步骤 4：运行测试验证通过** `npx vitest run tests/api.test.js` 预期：2 passed。
- [ ] **步骤 5：Commit** `git add frontend/src/api.js frontend/tests/api.test.js && git commit -m "feat(frontend): inject anon id and add detail apis"`

---

## 任务 6：前端 PostCard 可点击

**文件：** 修改 `frontend/src/components/PostCard.vue`；修改 `frontend/tests/PostListingComponents.test.js`。

- [ ] **步骤 1：编写失败的测试** 在 `PostListingComponents.test.js` 的 `describe('PostCard')` 末尾追加：

  ```js
  it('点击卡片 emit select', async () => {
    const w = mount(PostCard, { props: { post: { id: 7, title: 't', location: 'gulou', event_time: '2026-06-12T18:30:00', image_path: null } } })
    await w.get('[data-testid="post-card"]').trigger('click')
    expect(w.emitted().select[0][0]).toBe(7)
  })
  ```

- [ ] **步骤 2：运行测试验证失败** `npx vitest run tests/PostListingComponents.test.js` 预期：新用例 FAIL。
- [ ] **步骤 3：编写最少实现代码** `PostCard.vue` 根 `<article>` 加 `data-testid="post-card"`、`role="button"`、`tabindex="0"`、`@click="emit('select', props.post.id)"`、`@keydown.enter="..."`，`defineEmits(['select'])`，`.card { cursor: pointer; }`。
- [ ] **步骤 4：运行测试验证通过** `npx vitest run tests/PostListingComponents.test.js` 预期：原 6 + 新 1 = 7 passed。
- [ ] **步骤 5：Commit** `git add frontend/src/components/PostCard.vue frontend/tests/PostListingComponents.test.js && git commit -m "feat(frontend): make post card clickable"`

---

## 任务 7：前端 CommentForm 与 CommentList 组件

**文件：** 创建 `frontend/src/components/CommentForm.vue`、`CommentList.vue`；测试 `frontend/tests/CommentForm.test.js`、`CommentList.test.js`。

- [ ] **步骤 1：编写失败的测试**
  - `CommentForm.test.js`：空内容时 `[data-testid="comment-submit"]` 有 `disabled` 属性；`textarea.setValue('我也见过')` 后点击按钮 emit `submit` 含 `{ content: '我也见过', image: null }`。
  - `CommentList.test.js`：传入两条 items（`mine=true` 与 `mine=false`），仅渲染一条 `[data-testid^="comment-del-"]` 且为 `comment-del-1`；点击后 emit `delete` 含 id `1`。
- [ ] **步骤 2：运行测试验证失败** `npx vitest run tests/CommentForm.test.js tests/CommentList.test.js` 预期：组件不存在 FAIL。
- [ ] **步骤 3：编写最少实现代码**
  - `CommentForm.vue`：`<textarea v-model="content" maxlength=200>` + `<input type="file">`（jpg/png/webp、≤5MB）+ `<button data-testid="comment-submit" :disabled="content.trim()===''">评论</button>`；点击 emit `submit` `{ content: trim, image }` 后清空。
  - `CommentList.vue`：`<ul>` 渲染每条 `content / image_path 缩略图 / created_at`；`v-if="c.mine"` 渲染 `<button :data-testid="`comment-del-${c.id}`" @click="emit('delete', c.id)">删除</button>`。
- [ ] **步骤 4：运行测试验证通过** `npx vitest run tests/CommentForm.test.js tests/CommentList.test.js` 预期：4 passed。
- [ ] **步骤 5：Commit** `git add frontend/src/components/CommentForm.vue frontend/src/components/CommentList.vue frontend/tests/CommentForm.test.js frontend/tests/CommentList.test.js && git commit -m "feat(frontend): add comment form and list components"`

---

## 任务 8：前端 PostDetail 页面

**文件：** 创建 `frontend/src/components/PostDetail.vue`；测试 `frontend/tests/PostDetail.test.js`。

- [ ] **步骤 1：编写失败的测试** 新增 `PostDetail.test.js`，`vi.mock('../src/api.js')` 桩入 `getPost / toggleLike / listComments / createComment / deleteComment / imageUrl`。常量 `POST` 含完整字段（`contact_detail="微信 abc123"`、`like_count=1`、`liked_by_me=false`）。用例：
  - 默认隐藏 `contact_detail`：渲染后 `w.text()` 不含 “微信 abc123”；点击 `[data-testid="reveal-contact"]` 后包含。
  - 点赞按钮切换：mock `toggleLike` 返回 `{liked:true, like_count:2}`；点击 `[data-testid="like-btn"]` 后 `[data-testid="like-count"].text()==='2'` 且按钮文案含“已点赞”。
  - 评论提交：mock `createComment` 返回新评论；先 `listComments` 返回 `[]`，第二次返回含新评论。`textarea.setValue('我也见过')` → 点击 `[data-testid="comment-submit"]` → 断言 `createComment.mock.calls[0]` 为 `[1, { content: '我也见过', image: null }]`，页面文本含“我也见过”。
- [ ] **步骤 2：运行测试验证失败** `npx vitest run tests/PostDetail.test.js` 预期：组件不存在 FAIL。
- [ ] **步骤 3：编写最少实现代码** 新增 `PostDetail.vue`：
  - `defineProps({ postId: Number })`、`defineEmits(['back'])`。
  - `onMounted` 并行调用 `getPost(postId)`、`listComments(postId)`，分别写入 `post`、`comments`。
  - 顶部展示标题、寻物/寻主中文、物品种类中文、校区中文、丢失/捡到时间、描述、首图（用 `imageUrl`）。
  - `contact_type` 中文映射；按钮 `data-testid="reveal-contact"`，`v-if="!showContact"`，点击置 `true`，展开后展示 `post.contact_detail`。
  - 点赞按钮：`<button data-testid="like-btn" @click="onLike">{{ post.liked_by_me ? '已点赞' : '点赞' }}</button> <span data-testid="like-count">{{ post.like_count }}</span>`；`onLike` 调 `toggleLike(postId)` 后用返回值更新 `post`。
  - 顶部“返回”按钮 `@click="emit('back')"`。
  - `<CommentForm @submit="onSubmitComment" />`：`onSubmitComment(payload)` → `createComment(postId, payload)`，然后 `comments.value = await listComments(postId)`。
  - `<CommentList :items="comments" @delete="onDelete" />`：`onDelete(id)` → `confirm('确认删除？')` → `deleteComment(id)` → 重新 `listComments`。
- [ ] **步骤 4：运行测试验证通过** `npx vitest run tests/PostDetail.test.js` 预期：3 passed。
- [ ] **步骤 5：Commit** `git add frontend/src/components/PostDetail.vue frontend/tests/PostDetail.test.js && git commit -m "feat(frontend): add post detail view"`

---

## 任务 9：前端 App 集成详情视图

**文件：** 修改 `frontend/src/App.vue`、`frontend/src/components/PostList.vue`；修改 `frontend/tests/App.test.js`。

- [ ] **步骤 1：编写失败的测试** 在 `App.test.js` 现有 `vi.mock` 中补齐 `getPost / toggleLike / listComments / createComment / deleteComment / imageUrl` mock；新增用例：

  ```js
  it('点击列表卡片切换到 detail 视图', async () => {
    listPosts.mockResolvedValue([
      { id: 5, title: 'x', location: 'gulou', event_time: '2026-06-12T18:30:00', image_path: null }
    ])
    getPost.mockResolvedValue({ id: 5, post_type: 'lost', title: 'x', category: 'daily',
      image_path: null, description: '', location: 'gulou',
      event_time: '2026-06-12T18:30:00', contact_type: 'owner_contact',
      contact_detail: '...', created_at: '2026-06-13T10:00:00',
      like_count: 0, liked_by_me: false })
    listComments.mockResolvedValue([])
    const w = mount(App)
    await flushPromises()
    await w.get('[data-testid="post-card"]').trigger('click')
    await flushPromises()
    expect(w.findComponent({ name: 'PostDetail' }).exists()).toBe(true)
  })
  ```

- [ ] **步骤 2：运行测试验证失败** `npx vitest run tests/App.test.js` 预期：新用例 FAIL。
- [ ] **步骤 3：编写最少实现代码**
  - `PostList.vue`：`defineEmits(['select'])`，`<PostCard @select="(id) => emit('select', id)" />`。
  - `App.vue`：`import PostDetail from './components/PostDetail.vue'`；新增 `selectedPostId = ref(null)`；`<PostList ... @select="onSelectPost" />`；`onSelectPost(id) => { selectedPostId.value = id; view.value = 'detail' }`；新增分支 `<PostDetail v-else-if="view==='detail'" :post-id="selectedPostId" @back="backHome" />`；`backHome` 同时 `selectedPostId.value = null`。
- [ ] **步骤 4：运行测试验证通过** `npx vitest run tests/App.test.js` 预期：原 3 + 新 1 = 4 passed；`npm test` 全套绿。
- [ ] **步骤 5：Commit** `git add frontend/src/App.vue frontend/src/components/PostList.vue frontend/tests/App.test.js && git commit -m "feat(frontend): wire post detail view into app"`

---

## 任务 10：文档与全量验证

**文件：** 修改 `README.md`、`AGENT_LOG.md`。

- [ ] **步骤 1：更新文档** README 功能列表加“详情页 / 点赞 / 评论”，技术栈段刷新测试用例数（后端 33 → 50；前端 18 → 29）；AGENT_LOG 追加“2026-06-13 帖子详情与互动功能实现”章节，列 commit、TDD 节奏、最终验证结果。
- [ ] **步骤 2：全量验证** 顺序执行：
  - 后端：`cd backend; .\.venv\Scripts\python.exe -m pytest -v`，必须 50 passed。
  - 前端：`cd frontend; npm test`，必须 29 passed。
  - 构建：`cd frontend; npm run build`、`docker compose build` 全部成功。
- [ ] **步骤 3：Commit** `git add README.md AGENT_LOG.md && git commit -m "docs: record post detail interactions"`

---

## 自检

- 规格覆盖度：
  - SPEC §3.1 详情页 → 任务 2 + 8 + 9。
  - SPEC §3.2 点赞 → 任务 3 + 8。
  - SPEC §3.3 评论 → 任务 4 + 7 + 8。
  - SPEC §3.4 匿名身份 → 任务 2 (`get_anon_id`) + 5 (`ensureAnonId`)。
  - SPEC §6 数据模型 → 任务 1。
  - SPEC §9 验收 1-9 → 6/8/3/3/7/8/8/4/10。
- 占位符扫描：任务 7、8 的“最少实现代码”用结构化要点 + 关键代码段描述，无 TODO；其余任务有完整代码或精确文件改动。
- 类型一致性：`PostDetailOut` 继承 `PostOut` + `like_count / liked_by_me`；`LikeToggleOut` 字段在前后端测试中一致；`CommentOut` 字段贯通后端测试、前端 mock、前端组件 props。

---

## 执行交接

计划已完成并保存到 `docs/superpowers/plans/2026-06-13-post-detail-interactions-plan.md`。两种执行方式：

1. 子代理驱动（推荐）—— 每个任务调度一个新的子代理 + 两阶段审查。
2. 内联执行 —— 在当前会话中使用 `executing-plans` 批量执行并设有检查点。

选哪种方式？
