# Metrics collection

Live MVP metrics are gathered over SSH using **fixed allowlisted commands only** (no user-supplied command strings). See `app/ssh_client.py`.

## Commands

| Metric | Command | Notes |
|--------|---------|--------|
| CPU % | `head -n 1 /proc/stat; sleep 1; head -n 1 /proc/stat` | Two samples; busy % from idle delta |
| Memory | `cat /proc/meminfo` | Used ≈ Total − Available; shows used/total and % |
| Network | `cat /proc/net/dev` | Sum of rx/tx bytes across non-`lo` interfaces (totals, not rates) |
| Ports | `ss -lntu` | Listening TCP/UDP; informational only (up to 50 rows) |

Connection timeout ~5s; command timeout ~8s. Failures surface as **unreachable** — no stack traces or credentials in the UI.

## Dashboard vs detail

- **Dashboard:** status (reachable / unreachable) plus thin CPU % and memory % when reachable.
- **Server detail:** full MVP set (CPU, memory used/total, network rx/tx totals, listening ports).

Both pages auto-refresh about every **10 seconds**.

## CI / tests

Parsers are tested with fixture `/proc` and `ss` samples. CI does **not** open live SSH sessions (`SKIP_SSH` in tests).
