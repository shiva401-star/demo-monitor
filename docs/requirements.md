# PRD: Demo Monitoring Infrastructure (Linux Servers)

## 1. Overview

Local demo web app for internal L1/L2/L3 and app/infra teams to view live Linux server metrics **without SSH login**.

| Item | Detail |
|------|--------|
| Product | Demo Monitoring Infrastructure — Servers (Linux) |
| Type | Local demo only (run where Cursor is running) |
| Stack | Python, Flask, attractive dark-ops UI |
| Access | Read-only UI after sign-in |

## 2. Problem

Today, checking memory, CPU, network, and port usage means logging into each server. This demo gives a single read-only UI for those metrics.

## 3. Users

Internal teams only: L1, L2, L3, infrastructure, and application development. Single shared `admin` account for the demo.

## 4. Goals

- Sign in and browse server metrics in a read-only UI
- Add Linux servers with real SSH connection details
- Collect live metrics over SSH every **10 seconds**
- Keep setup and steps minimal for local demo use

## 5. Non-Goals (out of scope)

- Alerts / notifications
- Historical charts / metric history
- Multi-user roles or SSO
- HTTPS
- Docker deployment

## 6. Features

### 6.1 Read-only UI (dark ops)

- Dark operations-style theme
- All monitoring views are **read-only** (no remote shell, no config changes on targets)
- Minimum screens:
  1. **Login**
  2. **Dashboard** — list of monitored servers with high-level status/metrics
  3. **Server detail** — CPU, memory, network, ports for one host
  4. **Add server** — form to register a Linux host

### 6.2 Sign-in

- Default username: `admin`
- Password stored **hashed** (e.g. bcrypt), never plain text
- Demo credential (document in README when implementing): `admin` / `admin123` (or equivalent hashed at startup)
- Session-based login; logout available
- Unauthenticated users redirected to Login

### 6.3 Add Linux servers

Required fields:

| Field | Notes |
|-------|--------|
| Display name | Friendly label |
| Hostname / IP | Target host |
| SSH port | Default `22` |
| SSH username | Remote user |
| Auth | Password **or** private key path/content |

- Persist server inventory locally (e.g. SQLite)
- Store SSH secrets securely enough for a local demo (at minimum not in plain logs; prefer hashed app password and careful handling of SSH credentials)
- Validate that the host is reachable over SSH when adding (simple success/fail message)

### 6.4 Live metrics (MVP)

Collected over SSH from each added host, refreshed every **10 seconds**:

| Metric | Display |
|--------|---------|
| CPU | Usage % |
| Memory | Used / total (and %) |
| Network | Basic I/O (e.g. rx/tx rates or totals) |
| Ports | Listening / in-use port list |

No disk, uptime, or process list in MVP.

## 7. Technical constraints

- **Backend:** Python + Flask
- **Frontend:** Server-rendered or simple templates/static assets; dark-ops look
- **Collection:** SSH to remote Linux hosts (real metrics, not mock)
- **Refresh:** ~10s (page auto-refresh or lightweight poll)
- **Deploy:** Local only — run Flask on the Cursor machine; no container requirement
- **Data:** Local DB/file for users/servers; metrics are live, not historically stored

## 8. Minimal local run (implementation target)

1. Create/activate a Python venv and install dependencies (`flask`, SSH client lib, password hash lib, etc.)
2. Initialize local DB and ensure `admin` exists with hashed password
3. Start Flask (`python app.py` or `flask run`)
4. Open the UI in a browser (e.g. `http://127.0.0.1:5000`)
5. Sign in as `admin`, add a Linux server with SSH fields, view Dashboard / Server detail

## 9. Acceptance criteria

- [ ] Login works with `admin` and hashed password; wrong password rejected
- [ ] UI is dark-ops styled and read-only for monitoring
- [ ] User can add a Linux server with hostname/IP, SSH port, username, and key or password
- [ ] Dashboard lists servers; Server detail shows CPU, memory, network, ports
- [ ] Metrics refresh about every 10 seconds while viewing
- [ ] App runs locally with a short install/run path; no Docker/HTTPS/alerts/history/roles required

## 10. Open points for implementation

- Prefer password vs key auth as default in the Add Server form (support both)
- Exact commands used over SSH to gather CPU/memory/network/ports (e.g. `/proc`, `ss`, `free`)
- Whether failed SSH/collection shows a clear “unreachable” state on Dashboard
