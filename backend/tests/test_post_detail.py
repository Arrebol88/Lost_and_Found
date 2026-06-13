from sqlalchemy import inspect


def test_post_likes_table_exists(client):
    from app.database import engine
    insp = inspect(engine)
    assert "post_likes" in insp.get_table_names()
    cols = {c["name"] for c in insp.get_columns("post_likes")}
    assert {"id", "post_id", "anon_id", "created_at"}.issubset(cols)
    uniques = insp.get_unique_constraints("post_likes")
    assert any(set(u["column_names"]) == {"post_id", "anon_id"} for u in uniques)


def test_post_comments_table_exists(client):
    from app.database import engine
    insp = inspect(engine)
    assert "post_comments" in insp.get_table_names()
    cols = {c["name"] for c in insp.get_columns("post_comments")}
    assert {"id", "post_id", "anon_id", "content", "image_path", "created_at"}.issubset(cols)
