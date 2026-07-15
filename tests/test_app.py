import os
import tempfile

# Use an isolated throwaway database for the test run.
os.environ.setdefault(
    "ARGUS_DB_PATH", os.path.join(tempfile.gettempdir(), "argus_test.db")
)

from backend.api_server import app


def _client():
    return app.test_client()


def test_home():
    assert _client().get("/").status_code == 200


def test_signup_page():
    assert _client().get("/signup").status_code == 200


def test_health():
    response = _client().get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_stats_shape():
    body = _client().get("/stats").get_json()
    for key in ("total_events", "high", "medium", "low", "users"):
        assert key in body


def test_login_failure_returns_401():
    response = _client().post(
        "/login",
        json={"email": "nobody@example.com", "password": "wrong"},
    )
    assert response.status_code == 401
    assert response.get_json()["status"] == "fail"


def test_signup_then_login_roundtrip():
    client = _client()
    signup = client.post(
        "/signup",
        json={
            "name": "CI User",
            "email": "ci@example.com",
            "password": "secret",
            "role": "user",
        },
    )
    assert signup.status_code == 200
    assert signup.get_json()["status"] == "success"

    login = client.post(
        "/login",
        json={"email": "ci@example.com", "password": "secret"},
    )
    body = login.get_json()
    assert login.status_code == 200
    assert body["status"] == "success"
    assert body["role"] == "user"
    assert body["name"] == "CI User"


def test_duplicate_signup_rejected():
    client = _client()
    payload = {
        "name": "Dupe",
        "email": "dupe@example.com",
        "password": "secret",
        "role": "user",
    }
    assert client.post("/signup", json=payload).status_code == 200
    assert client.post("/signup", json=payload).status_code == 409


def test_start_returns_demo_detections():
    # No webcam/CV stack in CI -> demo analysis path returns detections.
    body = _client().get("/start").get_json()
    assert "detections" in body
    assert len(body["detections"]) >= 1
    assert all("activity" in d and "risk" in d for d in body["detections"])


def test_video_requires_a_file():
    assert _client().post("/video").status_code == 400


def test_video_demo_analysis():
    import io
    data = {"file": (io.BytesIO(b"not a real video"), "clip.mp4")}
    resp = _client().post("/video", data=data, content_type="multipart/form-data")
    assert resp.status_code == 200
    body = resp.get_json()
    assert len(body.get("detections", [])) >= 1


def test_password_is_hashed_not_plaintext():
    import sqlite3
    from backend import config

    client = _client()
    client.post(
        "/signup",
        json={
            "name": "Hash Me",
            "email": "hash@example.com",
            "password": "plaintextpw",
            "role": "user",
        },
    )
    conn = sqlite3.connect(config.DB_PATH)
    stored = conn.execute(
        "SELECT password FROM users WHERE email=?", ("hash@example.com",)
    ).fetchone()[0]
    conn.close()
    assert stored != "plaintextpw"
    assert len(stored) > 20
