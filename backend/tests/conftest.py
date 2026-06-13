import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path, monkeypatch):
    db_file = tmp_path / "test.db"
    uploads_dir = tmp_path / "uploads"
    uploads_dir.mkdir()
    monkeypatch.setenv("NJU_DB_URL", f"sqlite:///{db_file.as_posix()}")
    monkeypatch.setenv("NJU_UPLOAD_DIR", str(uploads_dir))

    # main 模块是单例 FastAPI app；每个用例只需重新调用 init_app_state()
    # 让 database.engine 指向当前临时 DB 文件
    from app import main
    main.init_app_state()
    return TestClient(main.app)
