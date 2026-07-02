from app.models import Admin


def test_login_success(client, db):
    admin = Admin(username="zuhal_admin")
    admin.set_password("correct-horse")
    db.session.add(admin)
    db.session.commit()

    resp = client.post(
        "/api/auth/login", json={"username": "zuhal_admin", "password": "correct-horse"}
    )
    assert resp.status_code == 200
    assert "access_token" in resp.get_json()


def test_login_wrong_password(client, db):
    admin = Admin(username="zuhal_admin")
    admin.set_password("correct-horse")
    db.session.add(admin)
    db.session.commit()

    resp = client.post(
        "/api/auth/login", json={"username": "zuhal_admin", "password": "wrong"}
    )
    assert resp.status_code == 401


def test_login_missing_fields(client):
    resp = client.post("/api/auth/login", json={"username": "x"})
    assert resp.status_code == 400


def test_me_requires_token(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401


def test_me_with_valid_token(client, auth_headers):
    resp = client.get("/api/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["username"] == "admin"


def test_protected_route_rejects_missing_token(client):
    resp = client.post("/api/seasons", json={"name": "Season 1", "year": 2026})
    assert resp.status_code == 401
