# 南哪寻宝（NJU LostFound）

南京大学失物招领与寻物启事平台。当前版本实现"发帖闭环"。

## 功能

- 首页一键发帖（无需登录）
- 寻物帖 / 寻主帖类型选择
- 9 类物品分类（电子产品类、个人证件与卡类、箱包与收纳、配饰、衣物、日常小件、办公与学习、运动与户外、个人护理与健康）
- 单图上传（jpg / png / webp，≤ 5 MB），后端做 MIME + magic bytes 双校验
- 寻主帖支持 自取 / 联系方式 / 已移交管理处 三种交付方式

## 技术栈

- 后端：FastAPI + SQLAlchemy + SQLite（WAL）
- 前端：Vue 3 + Vite + axios
- 测试：pytest + httpx（22 用例）；Vitest + @vue/test-utils（7 用例）
- 容器化：Docker + docker-compose
- CI：GitHub Actions

## 一键启动

```bash
docker compose up --build
```

- 前端：http://localhost:5173
- 后端 health：http://localhost:8000/api/health

## 本地开发

```bash
# 后端
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 前端（另开一个终端）
cd frontend
npm install
npm run dev
```

## 测试

```bash
make test          # 后端 + 前端
make test-backend
make test-frontend
```

## 目录结构

```
.
├── backend/                 FastAPI 服务
│   ├── app/
│   │   ├── main.py          应用入口（CORS、lifespan、static）
│   │   ├── database.py      SQLite 引擎（init 时创建）
│   │   ├── models.py        Post 表 + 4 个 CHECK 约束
│   │   ├── schemas.py       Pydantic v2，含跨字段校验
│   │   ├── storage.py       图片落盘（uuid + 日期分目录）
│   │   └── routers/posts.py POST /api/posts
│   ├── tests/               pytest，22 用例
│   ├── uploads/             图片存储（git ignored）
│   └── Dockerfile
├── frontend/                Vue 3 SPA
│   ├── src/
│   │   ├── App.vue          三态视图切换
│   │   ├── api.js           axios 封装
│   │   └── components/
│   │       ├── TypePicker.vue
│   │       └── PostForm.vue
│   ├── tests/               Vitest，7 用例
│   └── Dockerfile
├── docker-compose.yml
├── Makefile
├── .github/workflows/ci.yml
└── docs/superpowers/        SPEC + PLAN
```

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `NJU_DB_URL` | `sqlite:///./nju_lostfound.db` | SQLite 连接串 |
| `NJU_UPLOAD_DIR` | `./uploads` | 图片存储目录 |

## 文档

- [SPEC](docs/superpowers/specs/2026-06-13-post-creation-design.md)
- [PLAN](docs/superpowers/plans/2026-06-13-post-creation-plan.md)
- [AGENT_LOG](AGENT_LOG.md)
