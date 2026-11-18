"""Parse allowlisted SSH command output into MVP metric fields."""

from __future__ import annotations

from typing import Any


def _parse_meminfo(text: str) -> dict[str, Any]:
    values: dict[str, int] = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, rest = line.split(":", 1)
        parts = rest.split()
        if not parts:
            continue
        try:
            values[key.strip()] = int(parts[0]) * 1024  # kB → bytes
        except ValueError:
            continue
    total = values.get("MemTotal", 0)
    available = values.get("MemAvailable", values.get("MemFree", 0))
    used = max(total - available, 0) if total else 0
    pct = round((used / total) * 100, 1) if total else 0.0
    return {
        "total_bytes": total,
        "used_bytes": used,
        "percent": pct,
    }


def _cpu_line_fields(line: str) -> list[int] | None:
    parts = line.split()
    if not parts or parts[0] != "cpu":
        return None
    try:
        return [int(x) for x in parts[1:]]
    except ValueError:
        return None


def _parse_cpu(text: str) -> dict[str, Any]:
    lines = [ln for ln in text.splitlines() if ln.startswith("cpu ")]
    if len(lines) < 2:
        return {"percent": None}
    a = _cpu_line_fields(lines[0])
    b = _cpu_line_fields(lines[1])
    if not a or not b or len(a) < 4 or len(b) < 4:
        return {"percent": None}
    idle_a = a[3] + (a[4] if len(a) > 4 else 0)
    idle_b = b[3] + (b[4] if len(b) > 4 else 0)
    total_a = sum(a)
    total_b = sum(b)
    total_delta = total_b - total_a
    idle_delta = idle_b - idle_a
    if total_delta <= 0:
        return {"percent": 0.0}
    busy = 1.0 - (idle_delta / total_delta)
    return {"percent": round(max(0.0, min(100.0, busy * 100.0)), 1)}


def _parse_netdev(text: str) -> dict[str, Any]:
    rx = tx = 0
    for line in text.splitlines():
        if ":" not in line:
            continue
        iface, rest = line.split(":", 1)
        name = iface.strip()
        if name in ("lo",):
            continue
        cols = rest.split()
        if len(cols) < 9:
            continue
        try:
            rx += int(cols[0])
            tx += int(cols[8])
        except ValueError:
            continue
    return {"rx_bytes": rx, "tx_bytes": tx}


def _parse_ports(text: str) -> list[dict[str, str]]:
    # ss -lntu: Netid State Recv-Q Send-Q Local Address:Port Peer...
    ports: list[dict[str, str]] = []
    seen: set[str] = set()
    for line in text.splitlines()[1:]:
        cols = line.split()
        if len(cols) < 5:
            continue
        proto, state, local = cols[0], cols[1], cols[4]
        key = f"{proto}:{local}"
        if key in seen:
            continue
        seen.add(key)
        ports.append({"proto": proto, "local": local, "state": state})
        if len(ports) >= 50:
            break
    return ports


def parse_metrics(raw: dict[str, str]) -> dict[str, Any]:
    """Build MVP metric dict from raw outputs. Tolerates malformed data."""
    try:
        cpu = _parse_cpu(raw.get("cpu", ""))
    except Exception:
        cpu = {"percent": None}
    try:
        memory = _parse_meminfo(raw.get("mem", ""))
    except Exception:
        memory = {"total_bytes": 0, "used_bytes": 0, "percent": 0.0}
    try:
        network = _parse_netdev(raw.get("net", ""))
    except Exception:
        network = {"rx_bytes": 0, "tx_bytes": 0}
    try:
        ports = _parse_ports(raw.get("ports", ""))
    except Exception:
        ports = []
    return {
        "cpu": cpu,
        "memory": memory,
        "network": network,
        "ports": ports,
    }


def format_bytes(n: int) -> str:
    value = float(n)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if value < 1024 or unit == "TiB":
            if unit == "B":
                return f"{int(value)} {unit}"
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{n} B"
