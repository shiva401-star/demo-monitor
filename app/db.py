"""Local SQLite helpers. DB file is local-only and gitignored."""

from __future__ import annotations

import sqlite3
from typing import Any

from flask import Flask, current_app, g


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        conn = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        g.db = conn
    return g.db


def close_db(_e: BaseException | None = None) -> None:
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def init_db() -> None:
    db = get_db()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS servers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            display_name TEXT NOT NULL,
            host TEXT NOT NULL,
            ssh_port INTEGER NOT NULL DEFAULT 22,
            ssh_username TEXT NOT NULL,
            auth_type TEXT NOT NULL CHECK (auth_type IN ('password', 'key')),
            secret_encrypted TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )
    db.commit()


def query_one(sql: str, args: tuple[Any, ...] = ()) -> sqlite3.Row | None:
    return get_db().execute(sql, args).fetchone()


def query_all(sql: str, args: tuple[Any, ...] = ()) -> list[sqlite3.Row]:
    return get_db().execute(sql, args).fetchall()


def execute(sql: str, args: tuple[Any, ...] = ()) -> None:
    db = get_db()
    db.execute(sql, args)
    db.commit()


def init_app(app: Flask) -> None:
    app.teardown_appcontext(close_db)
