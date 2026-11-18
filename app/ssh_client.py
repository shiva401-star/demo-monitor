"""SSH helper: connect with timeouts, run allowlisted read-only commands only."""

from __future__ import annotations

import io
import logging
from typing import Any

import paramiko

logger = logging.getLogger(__name__)

# Fixed allowlist — never interpolate user input into command strings.
CMD_CPU_SAMPLE = "head -n 1 /proc/stat; sleep 1; head -n 1 /proc/stat"
CMD_MEMINFO = "cat /proc/meminfo"
CMD_NETDEV = "cat /proc/net/dev"
CMD_PORTS = "ss -lntu"

ALLOWLIST = frozenset({CMD_CPU_SAMPLE, CMD_MEMINFO, CMD_NETDEV, CMD_PORTS})

CONNECT_TIMEOUT = 5
COMMAND_TIMEOUT = 8


def _load_pkey(key_material: str) -> paramiko.PKey:
    buf = io.StringIO(key_material)
    last_error: Exception | None = None
    for loader in (
        paramiko.RSAKey.from_private_key,
        paramiko.Ed25519Key.from_private_key,
        paramiko.ECDSAKey.from_private_key,
    ):
        try:
            buf.seek(0)
            return loader(buf)
        except Exception as exc:  # noqa: BLE001 — try next key type
            last_error = exc
    raise ValueError("Unsupported or invalid private key") from last_error


def open_client(
    host: str,
    port: int,
    username: str,
    *,
    password: str | None = None,
    private_key: str | None = None,
    timeout: int = CONNECT_TIMEOUT,
) -> paramiko.SSHClient:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    kwargs: dict[str, Any] = {
        "hostname": host,
        "port": port,
        "username": username,
        "timeout": timeout,
        "allow_agent": False,
        "look_for_keys": False,
    }
    if private_key:
        kwargs["pkey"] = _load_pkey(private_key)
    elif password is not None:
        kwargs["password"] = password
    else:
        raise ValueError("password or private_key required")
    client.connect(**kwargs)
    return client


def run_allowlisted(client: paramiko.SSHClient, command: str) -> str:
    if command not in ALLOWLIST:
        raise ValueError("Command not allowlisted")
    _stdin, stdout, stderr = client.exec_command(command, timeout=COMMAND_TIMEOUT)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    code = stdout.channel.recv_exit_status()
    if code != 0 and not out:
        raise RuntimeError(err.strip() or f"remote command failed ({code})")
    return out


def check_connectivity(
    host: str,
    port: int,
    username: str,
    *,
    password: str | None = None,
    private_key: str | None = None,
) -> bool:
    """Return True if SSH auth succeeds. Never logs secrets."""
    client: paramiko.SSHClient | None = None
    try:
        client = open_client(
            host,
            port,
            username,
            password=password,
            private_key=private_key,
            timeout=CONNECT_TIMEOUT,
        )
        # Read-only probe
        run_allowlisted(client, CMD_MEMINFO)
        return True
    except Exception:
        logger.info("SSH connectivity check failed for %s:%s", host, port)
        return False
    finally:
        if client is not None:
            client.close()


def collect_raw_metrics(
    host: str,
    port: int,
    username: str,
    *,
    password: str | None = None,
    private_key: str | None = None,
) -> dict[str, str] | None:
    """Fetch raw command outputs. Returns None if unreachable."""
    client: paramiko.SSHClient | None = None
    try:
        client = open_client(
            host,
            port,
            username,
            password=password,
            private_key=private_key,
        )
        return {
            "cpu": run_allowlisted(client, CMD_CPU_SAMPLE),
            "mem": run_allowlisted(client, CMD_MEMINFO),
            "net": run_allowlisted(client, CMD_NETDEV),
            "ports": run_allowlisted(client, CMD_PORTS),
        }
    except Exception:
        logger.info("SSH metric collection failed for %s:%s", host, port)
        return None
    finally:
        if client is not None:
            client.close()
