"""Metric parser tests — fixture data only (no live SSH)."""

from __future__ import annotations

from app.metrics import parse_metrics
from app.ssh_client import ALLOWLIST, CMD_MEMINFO, run_allowlisted


SAMPLE_MEM = """
MemTotal:       8034908 kB
MemFree:        2000000 kB
MemAvailable:   4000000 kB
"""

SAMPLE_CPU = """cpu  100 0 100 800 0 0 0 0 0 0
cpu  120 0 120 820 0 0 0 0 0 0
"""

SAMPLE_NET = """Inter-|   Receive                                                |  Transmit
 face |bytes    packets errs drop fifo frame compressed multicast|bytes    packets errs drop fifo colls carrier compressed
    lo: 1000 1 0 0 0 0 0 0 1000 1 0 0 0 0 0 0
  eth0: 2000 2 0 0 0 0 0 0 3000 3 0 0 0 0 0 0
"""

SAMPLE_PORTS = """Netid State  Recv-Q Send-Q Local Address:Port Peer Address:Port
tcp   LISTEN 0      128          0.0.0.0:22        0.0.0.0:*
tcp   LISTEN 0      128             [::]:80           [::]:*
udp   UNCONN 0      0            0.0.0.0:68        0.0.0.0:*
"""


def test_parse_metrics_mvp_fields():
    result = parse_metrics(
        {
            "cpu": SAMPLE_CPU,
            "mem": SAMPLE_MEM,
            "net": SAMPLE_NET,
            "ports": SAMPLE_PORTS,
        }
    )
    assert result["cpu"]["percent"] is not None
    assert result["memory"]["total_bytes"] > 0
    assert result["memory"]["used_bytes"] > 0
    assert result["network"]["rx_bytes"] == 2000
    assert result["network"]["tx_bytes"] == 3000
    assert any(p["local"].endswith(":22") for p in result["ports"])


def test_parse_metrics_malformed_safe():
    result = parse_metrics({"cpu": "nope", "mem": "", "net": "x", "ports": ""})
    assert result["cpu"]["percent"] is None
    assert result["memory"]["total_bytes"] == 0
    assert result["ports"] == []


def test_allowlist_rejects_unknown_command():
    class Dummy:
        pass

    with __import__("pytest").raises(ValueError):
        run_allowlisted(Dummy(), "rm -rf /")  # type: ignore[arg-type]
    assert CMD_MEMINFO in ALLOWLIST
