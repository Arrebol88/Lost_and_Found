def test_health_ok(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_posts_table_exists(client):
    from sqlalchemy import inspect
    from app.database import engine
    insp = inspect(engine)
    assert "posts" in insp.get_table_names()
    cols = {c["name"] for c in insp.get_columns("posts")}
    expected = {
        "id", "post_type", "title", "category", "image_path",
        "description", "location", "event_time",
        "contact_type", "contact_detail", "created_at",
    }
    assert expected.issubset(cols)


def test_posts_table_has_location_check(client):
    from sqlalchemy import inspect
    from app.database import engine
    checks = inspect(engine).get_check_constraints("posts")
    sql = " ".join(c["sqltext"] for c in checks)
    assert "location IN ('gulou','xianlin','suzhou','pukou')" in sql
