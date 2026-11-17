# Demo Monitoring Infrastructure

Local dark-ops web UI for viewing live Linux server metrics over SSH — **read-only** after sign-in.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# for tests:
pip install -r requirements-dev.txt
```

Install only from the pinned `requirements.txt` / `requirements-dev.txt`. Do not commit `venv/`.

Optional: copy `.env.example` to `.env` and set `SECRET_KEY` (never commit `.env`).

## Run

Bind to loopback on port **5140** (5100 is often already taken on shared hosts):

```bash
source venv/bin/activate
export SECRET_KEY=dev-only-change-me   # placeholder for local demo
export FLASK_APP=app
export FLASK_RUN_HOST=127.0.0.1
export FLASK_RUN_PORT=5140
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

### Login / logout (local demo)

1. Open `/login`, enter the demo credentials, submit.
2. You are redirected to the Dashboard (monitoring UI is behind login; metrics views stay read-only).
3. Use **Logout** in the header to clear the session.

## Database

SQLite file: `instance/monitoring.db` (or `DATABASE_PATH` if set). Local-only; gitignored via `*.db`. Password hashes only — never plain text.

## Tests

```bash
source venv/bin/activate
pip install -r requirements-dev.txt
pytest
```

Tests use a temporary DB and dummy `SECRET_KEY` / demo password — not the real demo DB.

## UI theme

Dark-ops layout (header + content shell). Monitoring views are intended to stay **read-only** (no remote shell or target config changes from the UI). Protected screens require sign-in.

## UI (MVP)

1. **Login** — `/login`
2. **Dashboard** — `/dashboard` (login required)
3. **Server detail** — `/servers/<id>` (login required)
4. **Add server** — `/servers/add` (login required)

See [docs/requirements.md](docs/requirements.md) and [docs/TODO.md](docs/TODO.md).
