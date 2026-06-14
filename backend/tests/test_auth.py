from sqlalchemy import inspect


def test_users_table_exists(client):
    from app.database import engine
    cols = {c["name"] for c in inspect(engine).get_columns("users")}
    assert {"id", "username", "password_hash", "created_at"} <= cols


def test_password_hash_and_verify():
    from app.auth.password import hash_password, verify_password

    h = hash_password("hunter2")
    assert h != "hunter2"
    assert verify_password("hunter2", h) is True
    assert verify_password("wrong", h) is False


def test_jwt_round_trip():
    from app.auth.jwt_utils import create_token, decode_token

    token = create_token(user_id=42, username="alice")
    payload = decode_token(token)
    assert payload["sub"] == "42"
    assert payload["username"] == "alice"


def test_jwt_invalid_raises():
    import pytest

    from app.auth.jwt_utils import JwtError, decode_token

    with pytest.raises(JwtError):
        decode_token("not-a-token")


def _register(client, username="alice", password="hunter2"):
    return client.post(
        "/api/auth/register", json={"username": username, "password": password}
    )


def test_register_returns_token(client):
    r = _register(client)
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["user"]["username"] == "alice"
    assert isinstance(body["token"], str) and len(body["token"]) > 20


def test_register_duplicate_username_409(client):
    _register(client)
    again = _register(client)
    assert again.status_code == 409


def test_register_username_validation(client):
    too_short = client.post("/api/auth/register", json={"username": "ab", "password": "hunter2"})
    assert too_short.status_code == 422


def test_login_success_and_failure(client):
    _register(client)
    ok = client.post("/api/auth/login", json={"username": "alice", "password": "hunter2"})
    assert ok.status_code == 200
    bad = client.post("/api/auth/login", json={"username": "alice", "password": "wrong"})
    assert bad.status_code == 401
    nope = client.post("/api/auth/login", json={"username": "ghost", "password": "hunter2"})
    assert nope.status_code == 401


def test_me_requires_token(client):
    r = client.get("/api/auth/me")
    assert r.status_code == 401


def test_me_returns_current(client):
    token = _register(client).json()["token"]
    r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["username"] == "alice"
