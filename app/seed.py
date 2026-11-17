"""Seed demo data on first run."""

from __future__ import annotations

from flask import Flask

from app.auth import hash_password
from app.db import execute, query_one


def seed_admin_user(app: Flask) -> None:
    with app.app_context():
        row = query_one("SELECT id FROM users WHERE username = ?", ("admin",))
        if row is not None:
            return
        password = app.config["DEMO_PASSWORD"]
        execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            ("admin", hash_password(password)),
        )
