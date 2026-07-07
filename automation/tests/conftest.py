import os
import socket
import sys
import tempfile
import threading
import time

import pytest
import requests

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend"))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)


def _free_port() -> int:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


@pytest.fixture()
def live_backend():
    """
    Spins up the real Flask backend (file-based SQLite so it's visible across
    the test thread and the server thread) so BackendClient's real HTTP calls
    can be exercised end-to-end, the same way it will run against a real
    deployment — no mocking of requests/HTTP itself.
    """
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)
    os.environ["TEST_DATABASE_URL"] = f"sqlite:///{db_path}"

    # Import lazily, after sys.path/env are set up, and fresh per-test so the
    # module-level Flask/SQLAlchemy state doesn't leak between tests.
    for mod_name in list(sys.modules):
        if mod_name in ("app", "config") or mod_name.startswith("app."):
            del sys.modules[mod_name]

    from app import create_app
    from app.extensions import db as _db
    from app.models import Admin, Season, Week

    app = create_app("testing")
    with app.app_context():
        _db.create_all()
        admin = Admin(username="automation")
        admin.set_password("automation-pass")
        _db.session.add(admin)

        season = Season(name="Season 1", year=2026)
        _db.session.add(season)
        _db.session.flush()
        week = Week(season_id=season.id, week_number=1)
        _db.session.add(week)
        _db.session.commit()
        week_id = week.id

    port = _free_port()
    thread = threading.Thread(
        target=app.run,
        kwargs={"host": "127.0.0.1", "port": port, "use_reloader": False},
        daemon=True,
    )
    thread.start()

    base_url = f"http://127.0.0.1:{port}"
    for _ in range(50):
        try:
            requests.get(f"{base_url}/api/health", timeout=0.5)
            break
        except requests.exceptions.ConnectionError:
            time.sleep(0.1)

    yield {
        "base_url": base_url,
        "week_id": week_id,
        "username": "automation",
        "password": "automation-pass",
    }

    try:
        os.remove(db_path)
    except OSError:
        pass
