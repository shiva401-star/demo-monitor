"""Test fixtures — dummy secrets and isolated DB only."""

from __future__ import annotations

import pytest

from app import create_app


@pytest.fixture()
def app(tmp_path):
    db_path = tmp_path / "test.db"
    application = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret-key",
            "DATABASE": str(db_path),
            "DEMO_PASSWORD": "test-pass-ok",
        }
    )
    yield application


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def csrf_token(client):
    response = client.get("/login")
    assert response.status_code == 200
    with client.session_transaction() as sess:
        token = sess.get("_csrf_token")
    assert token
    return token


def login(client, password: str = "test-pass-ok", username: str = "admin"):
    """Helper: establish session via form POST. Does not print credentials."""
    client.get("/login")
    with client.session_transaction() as sess:
        token = sess["_csrf_token"]
    return client.post(
        "/login",
        data={"username": username, "password": password, "csrf_token": token},
        follow_redirects=False,
    )
