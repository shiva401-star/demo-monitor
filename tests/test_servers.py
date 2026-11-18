"""Server inventory + dashboard tests. Fake credentials; SKIP_SSH enabled."""

from __future__ import annotations

from tests.conftest import add_server, login


def test_dashboard_empty_state(client):
    login(client)
    response = client.get("/dashboard")
    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "No servers yet" in body
    assert "fake-secret" not in body
    assert "BEGIN" not in body


def test_add_server_and_dashboard_lists(client):
    login(client)
    response = add_server(client)
    assert response.status_code == 302
    assert "/servers/" in response.headers["Location"]

    dash = client.get("/dashboard")
    body = dash.get_data(as_text=True)
    assert dash.status_code == 200
    assert "lab-1" in body
    assert "10.0.0.5" in body
    assert "reachable" in body
    assert "fake-secret" not in body


def test_add_server_rejects_invalid_host(client):
    login(client)
    response = add_server(client, host="bad;host")
    assert response.status_code == 400
    body = response.get_data(as_text=True)
    assert "invalid" in body.lower() or "Invalid" in body


def test_add_server_rejects_bad_port(client):
    login(client)
    response = add_server(client, ssh_port="99999")
    assert response.status_code == 400


def test_server_detail_shows_metrics_without_secrets(client):
    login(client)
    add_server(client)
    detail = client.get("/servers/1")
    body = detail.get_data(as_text=True)
    assert detail.status_code == 200
    assert "CPU" in body
    assert "Memory" in body
    assert "fake-secret" not in body


def test_dashboard_requires_login(client):
    response = client.get("/dashboard")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]
