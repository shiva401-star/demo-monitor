"""Input validation for server inventory — no shell metacharacters."""

from __future__ import annotations

import ipaddress
import re
from typing import Any

# Characters that must never appear in host / SSH username (no shell injection).
_UNSAFE = re.compile(r"[;$`|&<>(){}\[\]\\\"'\n\r\t\0 ]")
_HOSTNAME = re.compile(
    r"^(?=.{1,253}$)(?!-)[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.?$"
)
_USERNAME = re.compile(r"^[A-Za-z0-9_.-]{1,64}$")


def _clean(value: str | None) -> str:
    return (value or "").strip()


def validate_display_name(value: str | None) -> str:
    name = _clean(value)
    if not name or len(name) > 120:
        raise ValueError("Display name is required (max 120 characters).")
    return name


def validate_host(value: str | None) -> str:
    host = _clean(value)
    if not host or len(host) > 253:
        raise ValueError("Hostname or IP is required.")
    if _UNSAFE.search(host):
        raise ValueError("Hostname/IP contains invalid characters.")
    try:
        ipaddress.ip_address(host)
        return host
    except ValueError:
        pass
    if not _HOSTNAME.match(host):
        raise ValueError("Invalid hostname or IP address.")
    return host


def validate_port(value: Any) -> int:
    try:
        port = int(str(value).strip())
    except (TypeError, ValueError) as exc:
        raise ValueError("SSH port must be an integer.") from exc
    if port < 1 or port > 65535:
        raise ValueError("SSH port must be between 1 and 65535.")
    return port


def validate_username(value: str | None) -> str:
    username = _clean(value)
    if not username:
        raise ValueError("SSH username is required.")
    if _UNSAFE.search(username) or not _USERNAME.match(username):
        raise ValueError("SSH username contains invalid characters.")
    return username


def validate_auth(
    auth_type: str | None,
    password: str | None,
    private_key: str | None,
) -> tuple[str, str]:
    kind = _clean(auth_type).lower() or "password"
    if kind not in ("password", "key"):
        raise ValueError("Auth type must be password or key.")
    if kind == "password":
        secret = password or ""
        if not secret:
            raise ValueError("SSH password is required for password auth.")
        if len(secret) > 1024:
            raise ValueError("SSH password is too long.")
        return kind, secret
    secret = (private_key or "").strip()
    if not secret:
        raise ValueError("Private key content is required for key auth.")
    if len(secret) > 32_000:
        raise ValueError("Private key is too large.")
    if "PRIVATE KEY" not in secret.upper():
        raise ValueError("Private key does not look like a PEM key.")
    return kind, secret


def parse_server_form(form: Any) -> dict[str, Any]:
    """Validate Add Server form fields. Raises ValueError on failure."""
    auth_type, secret = validate_auth(
        form.get("auth_type"),
        form.get("ssh_password"),
        form.get("ssh_private_key"),
    )
    return {
        "display_name": validate_display_name(form.get("display_name")),
        "host": validate_host(form.get("host")),
        "ssh_port": validate_port(form.get("ssh_port") or "22"),
        "ssh_username": validate_username(form.get("ssh_username")),
        "auth_type": auth_type,
        "secret": secret,
    }
