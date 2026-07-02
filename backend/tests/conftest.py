import pytest
from app import create_app
from app.extensions import db as _db
from app.models import Admin


@pytest.fixture()
def app():
    app = create_app("testing")
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def db(app):
    return _db


@pytest.fixture()
def auth_headers(app, client, db):
    admin = Admin(username="admin")
    admin.set_password("supersecret")
    db.session.add(admin)
    db.session.commit()

    resp = client.post(
        "/api/auth/login", json={"username": "admin", "password": "supersecret"}
    )
    token = resp.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
