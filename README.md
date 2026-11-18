# Demo Monitoring Infrastructure

Local dark-ops web UI for viewing live Linux server metrics over SSH — **read-only** after sign-in.

Docs: [PRD](docs/requirements.md) · [TODO](docs/TODO.md) · [Metrics](docs/metrics.md) · [CI](docs/ci.md)

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# for tests:
pip install -r requirements-dev.txt
```

Install only from the pinned `requirements.txt` / `requirements-dev.txt`. Do not commit `venv/`, `.env`, `instance/`, `*.db`, or private keys.

Optional: copy `.env.example` to `.env` and set `SECRET_KEY` (never commit `.env`).

## Run (local demo)

```bash
source venv/bin/activate
export SECRET_KEY=dev-only-change-me
export FLASK_APP=app
flask run --host 127.0.0.1 --port 5140
# or: python -m app
```

Open [http://127.0.0.1:5140](http://127.0.0.1:5140).

## Demo login

| Field | Value |
|-------|--------|
| Username | `admin` |
| Password | `admin123` |

Override the seed password with `DEMO_PASSWORD` before first run if desired.

1. Open `/login`, sign in, go to Dashboard.
2. **Add server** with hostname/IP, SSH port (default 22), username, and password or PEM key.
3. Open a server from the Dashboard for CPU, memory, network, and ports (auto-refresh ~10s).
4. **Logout** clears the session.

SSH credentials are stored encrypted locally in SQLite and are never shown in the UI or committed to git.

## Add server fields

| Field | Notes |
|-------|--------|
| Display name | Friendly label |
| Hostname / IP | Target Linux host |
| SSH port | Default `22` |
| SSH username | Remote user |
| Auth | Password **or** private key (PEM) |

On submit the app checks SSH reachability. Failure means unreachable / auth failed (no stack traces).

## Dashboard

Columns: name, host, port, status (`reachable` / `unreachable`), CPU %, memory %. Detail pages add network totals and listening ports. Secrets are never listed.

## Database

SQLite: `instance/monitoring.db` (or `DATABASE_PATH`). Local-only; gitignored. Admin password is hashed; SSH secrets are encrypted with a key derived from `SECRET_KEY`.

## Tests

```bash
pytest
```

Uses a temp DB, dummy secrets, and `SKIP_SSH` (fixture parsers — no live SSH in CI).

## CI

GitHub Actions runs install + `pytest` on push/PR. **No deploy** — run locally only. See [docs/ci.md](docs/ci.md).

## Troubleshooting

| Symptom | What to try |
|---------|-------------|
| Login fails | Use `admin` / `admin123`, or the `DEMO_PASSWORD` you set before first DB create |
| SSH add fails | Host reachable? Port open? User/key/password correct? |
| Blank metrics | Status `unreachable` — fix SSH; UI stays read-only |

## UI (MVP)

1. **Login** — `/login`
2. **Dashboard** — `/dashboard`
3. **Server detail** — `/servers/<id>`
4. **Add server** — `/servers/add`
