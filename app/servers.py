"""Server inventory helpers. Secrets never logged or returned to templates."""

from __future__ import annotations

import os
from typing import Any

from flask import current_app

from app.crypto import decrypt_secret, encrypt_secret
from app.db import get_db, query_all, query_one
from app.metrics import parse_metrics
from app.ssh_client import check_connectivity, collect_raw_metrics


def create_server(data: dict[str, Any]) -> int:
    encrypted = encrypt_secret(data["secret"])
    db = get_db()
    cur = db.execute(
        """
        INSERT INTO servers (
            display_name, host, ssh_port, ssh_username, auth_type, secret_encrypted
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            data["display_name"],
            data["host"],
            data["ssh_port"],
            data["ssh_username"],
            data["auth_type"],
            encrypted,
        ),
    )
    db.commit()
    try:
        os.chmod(current_app.config["DATABASE"], 0o600)
    except OSError:
        pass
    return int(cur.lastrowid)


def list_servers() -> list[dict[str, Any]]:
    rows = query_all(
        """
        SELECT id, display_name, host, ssh_port, ssh_username, auth_type, created_at
        FROM servers
        ORDER BY id ASC
        """
    )
    return [dict(r) for r in rows]


def get_server(server_id: int) -> dict[str, Any] | None:
    row = query_one(
        """
        SELECT id, display_name, host, ssh_port, ssh_username, auth_type, created_at
        FROM servers WHERE id = ?
        """,
        (server_id,),
    )
    return dict(row) if row else None


def _credentials(server_id: int) -> tuple[dict[str, Any], str] | None:
    row = query_one(
        """
        SELECT id, display_name, host, ssh_port, ssh_username, auth_type, secret_encrypted
        FROM servers WHERE id = ?
        """,
        (server_id,),
    )
    if row is None:
        return None
    secret = decrypt_secret(row["secret_encrypted"])
    meta = {
        "id": row["id"],
        "display_name": row["display_name"],
        "host": row["host"],
        "ssh_port": row["ssh_port"],
        "ssh_username": row["ssh_username"],
        "auth_type": row["auth_type"],
    }
    return meta, secret


def _auth_kwargs(auth_type: str, secret: str) -> dict[str, str | None]:
    if auth_type == "key":
        return {"private_key": secret, "password": None}
    return {"password": secret, "private_key": None}


def probe_reachable(server_id: int) -> bool:
    if current_app.config.get("SKIP_SSH"):
        return True
    loaded = _credentials(server_id)
    if loaded is None:
        return False
    meta, secret = loaded
    return check_connectivity(
        meta["host"],
        meta["ssh_port"],
        meta["ssh_username"],
        **_auth_kwargs(meta["auth_type"], secret),
    )


def check_new_server_reachable(data: dict[str, Any]) -> bool:
    if current_app.config.get("SKIP_SSH"):
        return True
    return check_connectivity(
        data["host"],
        data["ssh_port"],
        data["ssh_username"],
        **_auth_kwargs(data["auth_type"], data["secret"]),
    )


def fetch_metrics_for(server_id: int) -> dict[str, Any] | None:
    if current_app.config.get("SKIP_SSH"):
        return {
            "cpu": {"percent": 12.5},
            "memory": {
                "total_bytes": 8_589_934_592,
                "used_bytes": 3_221_225_472,
                "percent": 37.5,
            },
            "network": {"rx_bytes": 1_000_000, "tx_bytes": 500_000},
            "ports": [
                {"proto": "tcp", "local": "0.0.0.0:22", "state": "LISTEN"},
            ],
        }
    loaded = _credentials(server_id)
    if loaded is None:
        return None
    meta, secret = loaded
    raw = collect_raw_metrics(
        meta["host"],
        meta["ssh_port"],
        meta["ssh_username"],
        **_auth_kwargs(meta["auth_type"], secret),
    )
    if raw is None:
        return None
    return parse_metrics(raw)


def dashboard_rows() -> list[dict[str, Any]]:
    """Servers with reachability and thin metric summary (no secrets)."""
    rows = []
    for server in list_servers():
        reachable = probe_reachable(server["id"])
        summary: dict[str, Any] = {
            **server,
            "status": "reachable" if reachable else "unreachable",
            "cpu_percent": None,
            "mem_percent": None,
        }
        if reachable:
            metrics = fetch_metrics_for(server["id"])
            if metrics:
                summary["cpu_percent"] = metrics["cpu"].get("percent")
                summary["mem_percent"] = metrics["memory"].get("percent")
        rows.append(summary)
    return rows
