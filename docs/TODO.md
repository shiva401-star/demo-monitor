# TODO: Demo Monitoring Infrastructure (Linux)

Small, AI-friendly increments. Complete in order. Each step includes **security** and **docs**. Local demo only (run where Cursor runs). See [requirements.md](requirements.md).

---

## Phase 0 — Project initialization and basic UI

- [x] **0.1** Create Python project layout (`app/`, `tests/`, `docs/`, `templates/`, `static/`)
  - Security: Add `.gitignore` for `.env`, `venv/`, `*.db`, `__pycache__/`, secrets, private keys
  - Docs: Short `README.md` with project name and one-line purpose

- [x] **0.2** Add `requirements.txt` with Flask (pin versions) and create/activate a local venv
  - Security: Do not commit `venv/`; document install from lock/pin file only
  - Docs: README — “create venv + `pip install -r requirements.txt`”

- [x] **0.3** Minimal Flask app that serves a dark-ops home page at `/`
  - Security: Set a placeholder `SECRET_KEY` via env (never hardcode a production secret); bind to `127.0.0.1` for local demo
  - Docs: README — how to start (`flask run` / `python -m app`) and open `http://127.0.0.1:5140`

- [x] **0.4** Add shared dark-ops base template + CSS (layout shell only: header, content area)
  - Security: No inline user-controlled HTML; use Jinja auto-escaping (default on)
  - Docs: Note UI theme (dark ops) and read-only intent in README

- [x] **0.5** Stub screens as empty/read-only pages: Login, Dashboard, Server detail, Add server (no logic yet)
  - Security: Links only; no forms that mutate data yet; no remote commands
  - Docs: List the four screens in README under “UI (MVP)”

---

## Phase 1 — Sign-in and unit tests

- [x] **1.1** Add local SQLite (or equivalent) and a `users` table
  - Security: Store password **hash only** (bcrypt/werkzeug); never plain text
  - Docs: Document DB file location and that it is local-only / gitignored

- [x] **1.2** Seed default user `admin` with hashed demo password on first run
  - Security: Hash at seed time; document demo password only in README (not in code comments committed as plain login hints next to hash logic if avoidable)
  - Docs: README — demo login `admin` / agreed demo password

- [x] **1.3** Implement Login form (POST) + session cookie + Logout
  - Security: HttpOnly session cookie; CSRF token on login form; constant-time password check via library; redirect unauthenticated users to Login
  - Docs: README — login/logout steps for local demo

- [x] **1.4** Protect Dashboard / Server detail / Add server routes (login required)
  - Security: Server-side session check on every protected route; no client-only “auth”
  - Docs: Note that monitoring UI is behind login and remains read-only for metrics views

- [x] **1.5** Unit tests for auth (hash verify, login success/fail, logout, protected route redirect)
  - Security: Tests must not log passwords; use test DB, not the real demo DB
  - Docs: README — how to run tests (`pytest`)

- [x] **1.6** Wire test runner locally (`pytest`, `requirements-dev.txt` if needed)
  - Security: Ensure secrets/env fixtures are dummy values in tests
  - Docs: One-line “run tests” in README

---

## Phase 2 — CI/CD (GitHub Actions)

- [ ] **2.1** Add `.github/workflows/ci.yml` — install deps, run lint (optional light), run `pytest` on PR/push
  - Security: No secrets in workflow logs; use dummy env for `SECRET_KEY`; do not upload DB/artifacts with credentials
  - Docs: Short `docs/ci.md` or README section — what CI runs

- [ ] **2.2** Keep CI minimal (no deploy job — local demo only)
  - Security: No SSH keys or host credentials in GitHub Secrets for this demo
  - Docs: Explicitly state “no CD deploy; run locally”

---

## Phase 3 — Server inventory (Add server)

- [ ] **3.1** Add `servers` table (display name, host, SSH port, username, auth type)
  - Security: Separate column(s) for secrets; never commit DB; prepare to encrypt or at least avoid logging secrets
  - Docs: Document required fields (aligned with PRD)

- [ ] **3.2** Add Server form UI (name, hostname/IP, port default 22, username, password **or** key)
  - Security: CSRF on form; mask password/key inputs; do not echo secrets back in HTML
  - Docs: Screenshot-free field list in README

- [ ] **3.3** Persist new server (password or key material) with basic validation
  - Security: Store SSH password/key encrypted at rest if practical for demo; never write secrets to app logs; restrict file perms on DB
  - Docs: Warn that SSH credentials stay on the local machine only

- [ ] **3.4** On add: SSH connectivity check (success/fail message only)
  - Security: Timeout SSH; disallow shell metacharacters in host/user; use parametrized SSH library (e.g. Paramiko), not `os.system`
  - Docs: Note failure means “unreachable / auth failed” — no stack traces to UI

- [ ] **3.5** Unit tests for server validation and “reject invalid host/port”
  - Security: Tests use fake credentials; no real key files in repo
  - Docs: Mention test coverage for inventory validation

---

## Phase 4 — Dashboard (read-only list)

- [ ] **4.1** Dashboard lists saved servers (name, host, port, status placeholder)
  - Security: Require login; never show SSH passwords/keys on dashboard
  - Docs: Describe dashboard columns in README

- [ ] **4.2** Show simple status (reachable / unreachable) without full metrics yet
  - Security: Short SSH timeout; no retry storms; read-only checks only
  - Docs: Define status meanings

- [ ] **4.3** Unit tests for dashboard route auth and empty-state
  - Security: Assert secrets absent from response body
  - Docs: Keep test run instructions up to date

---

## Phase 5 — Live metrics over SSH (MVP)

- [ ] **5.1** SSH helper module: connect, run **fixed** read-only commands, disconnect
  - Security: Allowlist commands only (CPU/mem/net/ports); no user-supplied command strings; connection timeouts
  - Docs: Document exact commands used (`/proc`, `free`, `ss`, etc.) in `docs/metrics.md`

- [ ] **5.2** Collect CPU % and memory used/total
  - Security: Parse command output safely; handle malformed output without crashing
  - Docs: Update `docs/metrics.md` with field definitions

- [ ] **5.3** Collect basic network I/O and listening ports
  - Security: Read-only; do not expose service banners beyond port/process basics needed for demo
  - Docs: Note ports list is informational only

- [ ] **5.4** Server detail page renders MVP metrics
  - Security: Login required; no remote write actions; escape all displayed values
  - Docs: README — how to open Server detail from Dashboard

- [ ] **5.5** Auto-refresh metrics every **10 seconds** (meta refresh or light poll)
  - Security: Poll only authenticated endpoints; rate already fixed at 10s; no open unauthenticated JSON API
  - Docs: State refresh interval in README

- [ ] **5.6** Dashboard high-level metric snapshot (optional thin summary from same collector)
  - Security: Same allowlisted collector; no secrets in JSON/HTML
  - Docs: Clarify dashboard vs detail metric depth

- [ ] **5.7** Unit tests for metric parsers (sample `/proc` / command fixtures) + unreachable host handling
  - Security: Fixture data only; no live SSH required in CI
  - Docs: Note CI uses fixtures, not real servers

---

## Phase 6 — Hardening and demo polish

- [ ] **6.1** Centralize config via env (secret key, DB path, demo password override for local only)
  - Security: Fail fast if `SECRET_KEY` missing in non-dev; document safe local defaults
  - Docs: `.env.example` with dummy values (no real passwords/keys)

- [ ] **6.2** Uniform error pages / flash messages (no tracebacks in browser)
  - Security: Hide internals; log errors server-side without credentials
  - Docs: Troubleshooting blurb (login fail, SSH fail)

- [ ] **6.3** Final README pass: clone/venv/install/run/login/add server/view metrics (minimal steps)
  - Security: Remind users not to commit `.env`, DB, or private keys
  - Docs: Link PRD + this TODO; mark MVP complete

- [ ] **6.4** Confirm CI green and acceptance criteria from PRD checked off
  - Security: Quick review — CSRF, hashed admin password, no secrets in repo, SSH allowlist
  - Docs: Checkboxes in PRD §9 updated when done

---

## Suggested implement-one-increment rule

When using AI assistance: **one checkbox per change set** (code + security note + doc touch), run relevant tests, then move to the next box.
