"""Auth helpers: password hashes, session gate, CSRF."""

from __future__ import annotations

import hmac
import secrets
from functools import wraps
from typing import Any, Callable, TypeVar

from flask import flash, redirect, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

F = TypeVar("F", bound=Callable[..., Any])

SESSION_USER_KEY = "user_id"
SESSION_USERNAME_KEY = "username"
CSRF_SESSION_KEY = "_csrf_token"


def hash_password(password: str) -> str:
    return generate_password_hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    return check_password_hash(password_hash, password)


def login_user(user_id: int, username: str) -> None:
    session.clear()
    session[SESSION_USER_KEY] = user_id
    session[SESSION_USERNAME_KEY] = username
    session.permanent = False
    rotate_csrf_token()


def logout_user() -> None:
    session.clear()


def current_user_id() -> int | None:
    return session.get(SESSION_USER_KEY)


def is_authenticated() -> bool:
    return current_user_id() is not None


def login_required(view: F) -> F:
    @wraps(view)
    def wrapped(*args: Any, **kwargs: Any):
        if not is_authenticated():
            flash("Please sign in to continue.", "error")
            return redirect(url_for("main.login", next=request.path))
        return view(*args, **kwargs)

    return wrapped  # type: ignore[return-value]


def get_csrf_token() -> str:
    token = session.get(CSRF_SESSION_KEY)
    if not token:
        token = rotate_csrf_token()
    return token


def rotate_csrf_token() -> str:
    token = secrets.token_hex(32)
    session[CSRF_SESSION_KEY] = token
    return token


def validate_csrf_token(token: str | None) -> bool:
    expected = session.get(CSRF_SESSION_KEY)
    if not expected or not token:
        return False
    return hmac.compare_digest(expected, token)
