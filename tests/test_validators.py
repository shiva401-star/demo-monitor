"""Inventory validation tests — fake credentials only."""

from __future__ import annotations

import pytest

from app.validators import (
    parse_server_form,
    validate_host,
    validate_port,
    validate_username,
)


def test_validate_host_accepts_ip_and_hostname():
    assert validate_host("10.0.0.1") == "10.0.0.1"
    assert validate_host("lab.example.com") == "lab.example.com"


def test_validate_host_rejects_metacharacters():
    with pytest.raises(ValueError):
        validate_host("host;rm -rf /")
    with pytest.raises(ValueError):
        validate_host("host$(reboot)")


def test_validate_port_bounds():
    assert validate_port("22") == 22
    with pytest.raises(ValueError):
        validate_port("0")
    with pytest.raises(ValueError):
        validate_port("70000")
    with pytest.raises(ValueError):
        validate_port("abc")


def test_validate_username_rejects_unsafe():
    assert validate_username("ubuntu") == "ubuntu"
    with pytest.raises(ValueError):
        validate_username("bad;user")


def test_parse_server_form_password_ok():
    data = parse_server_form(
        {
            "display_name": "web-1",
            "host": "192.168.1.10",
            "ssh_port": "22",
            "ssh_username": "ops",
            "auth_type": "password",
            "ssh_password": "fake-only",
            "ssh_private_key": "",
        }
    )
    assert data["host"] == "192.168.1.10"
    assert data["auth_type"] == "password"
    assert data["secret"] == "fake-only"


def test_parse_server_form_rejects_empty_password():
    with pytest.raises(ValueError):
        parse_server_form(
            {
                "display_name": "web-1",
                "host": "192.168.1.10",
                "ssh_port": "22",
                "ssh_username": "ops",
                "auth_type": "password",
                "ssh_password": "",
                "ssh_private_key": "",
            }
        )
