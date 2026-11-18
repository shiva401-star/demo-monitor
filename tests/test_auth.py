"""Auth unit tests. Credentials are never logged."""

from __future__ import annotations

from app.auth import hash_password, verify_password
from tests.conftest import login


def test_hash_verify_roundtrip():
    digest = hash_password("sample-value")
    assert digest != "sample-value"
    assert verify_password(digest, "sample-value") is True
    assert verify_password(digest, "wrong-value") is False


def test_login_success(client):
    response = login(client)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard")
    with client.session_transaction() as sess:
        assert sess.get("user_id") is not None
        assert sess.get("username") == "admin"


def test_login_failure_bad_password(client):
    response = login(client, password="not-the-password")
    assert response.status_code == 401
    with client.session_transaction() as sess:
        assert sess.get("user_id") is None


def test_login_failure_unknown_user(client):
    response = login(client, username="nobody")
    assert response.status_code == 401
    with client.session_transaction() as sess:
        assert sess.get("user_id") is None


def test_login_rejects_bad_csrf(client):
    client.get("/login")
    response = client.post(
        "/login",
        data={
            "username": "admin",
            "password": "test-pass-ok",
            "csrf_token": "tampered",
        },
    )
    assert response.status_code == 400
    with client.session_transaction() as sess:
        assert sess.get("user_id") is None


def test_logout_clears_session(client):
    login(client)
    with client.session_transaction() as sess:
        token = sess["_csrf_token"]
    response = client.post("/logout", data={"csrf_token": token})
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")
    with client.session_transaction() as sess:
        assert sess.get("user_id") is None


def test_protected_routes_redirect_when_anonymous(client):
    for path in ("/dashboard", "/servers/1", "/servers/add"):
        response = client.get(path)
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]


def test_protected_routes_ok_when_authenticated(client):
    login(client)
    assert client.get("/dashboard").status_code == 200
    assert client.get("/servers/add").status_code == 200
    # No server id 1 yet → 404 page (still authenticated)
    assert client.get("/servers/1").status_code == 404


def test_session_cookie_httponly_configured(app):
    assert app.config["SESSION_COOKIE_HTTPONLY"] is True
