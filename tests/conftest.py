"""Test fixtures — dummy secrets, isolated DB, no live SSH."""

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
            "SKIP_SSH": True,
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


def add_server(
    client,
    *,
    display_name: str = "lab-1",
    host: str = "10.0.0.5",
    ssh_port: str = "22",
    ssh_username: str = "monitor",
    auth_type: str = "password",
    ssh_password: str = "fake-secret",
    ssh_private_key: str = "",
):
    client.get("/servers/add")
    with client.session_transaction() as sess:
        token = sess["_csrf_token"]
    data = {
        "csrf_token": token,
        "display_name": display_name,
        "host": host,
        "ssh_port": ssh_port,
        "ssh_username": ssh_username,
        "auth_type": auth_type,
        "ssh_password": ssh_password,
        "ssh_private_key": ssh_private_key,
    }
    return client.post("/servers/add", data=data, follow_redirects=False)
