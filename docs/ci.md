# CI

## What runs

GitHub Actions workflow [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) on push to `main` and on pull requests:

1. Install pinned deps from `requirements-dev.txt`
2. Light check: `python -m compileall`
3. `pytest` (auth, inventory validation, metric parsers — **fixture data only**, no live SSH)

CI uses dummy `SECRET_KEY` / `DEMO_PASSWORD` env vars. No SSH keys or host credentials are stored in GitHub Secrets for this demo.

## Deploy

**No CD deploy job.** This is a local demo — run Flask on the machine where Cursor is running. See the README.
