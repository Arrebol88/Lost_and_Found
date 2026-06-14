import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path, monkeypatch):
    db_file = tmp_path / "test.db"
    uploads_dir = tmp_path / "uploads"
    uploads_dir.mkdir()
    monkeypatch.setenv("NJU_DB_URL", f"sqlite:///{db_file.as_posix()}")
    monkeypatch.setenv("NJU_UPLOAD_DIR", str(uploads_dir))
    monkeypatch.setenv("JWT_SECRET", "test-secret")

    from app import main
    main.init_app_state()
    return TestClient(main.app)


@pytest.fixture()
def auth(client):
    """注册并登录指定用户名，返回带 Bearer token 的 headers。"""

    cache: dict[str, dict] = {}

    def _make(username: str = "alice", password: str = "hunter2") -> dict:
        if username in cache:
            return cache[username]
        client.post("/api/auth/register", json={"username": username, "password": password})
        resp = client.post("/api/auth/login", json={"username": username, "password": password})
        token = resp.json()["token"]
        cache[username] = {"Authorization": f"Bearer {token}"}
        return cache[username]

    return _make


@pytest.fixture()
def headers(client, auth):
    """默认作者 alice 的鉴权 header（保持与旧 anon_id 用法接近的便捷别名）。"""
    return auth("alice")
