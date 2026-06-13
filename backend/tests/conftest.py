import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path, monkeypatch):
    db_file = tmp_path / "test.db"
    uploads_dir = tmp_path / "uploads"
    uploads_dir.mkdir()
    monkeypatch.setenv("NJU_DB_URL", f"sqlite:///{db_file.as_posix()}")
    monkeypatch.setenv("NJU_UPLOAD_DIR", str(uploads_dir))

    # 重新加载模块以读取环境变量
    import importlib
    from app import database
    importlib.reload(database)
    from app import main
    importlib.reload(main)

    main.init_app_state()
    return TestClient(main.app)
