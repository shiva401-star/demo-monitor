"""App routes: home, auth, and protected monitoring stubs."""

from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.auth import (
    login_required,
    login_user,
    logout_user,
    validate_csrf_token,
    verify_password,
)
from app.db import query_one

bp = Blueprint("main", __name__)


@bp.get("/")
def home():
    return render_template("home.html")


def _safe_next_url(raw: str | None) -> str:
    next_url = (raw or "").strip() or url_for("main.dashboard")
    if not next_url.startswith("/") or next_url.startswith("//"):
        return url_for("main.dashboard")
    return next_url


@bp.route("/login", methods=["GET", "POST"])
def login():
    from app.auth import is_authenticated

    if request.method == "GET":
        if is_authenticated():
            return redirect(_safe_next_url(request.args.get("next")))
        return render_template("login.html")

    if not validate_csrf_token(request.form.get("csrf_token")):
        flash("Invalid session token. Try again.", "error")
        return render_template("login.html"), 400

    username = (request.form.get("username") or "").strip()
    password = request.form.get("password") or ""

    user = query_one(
        "SELECT id, username, password_hash FROM users WHERE username = ?",
        (username,),
    )
    if user is None or not verify_password(user["password_hash"], password):
        flash("Invalid username or password.", "error")
        return render_template("login.html"), 401

    login_user(user["id"], user["username"])
    flash("Signed in.", "ok")
    return redirect(_safe_next_url(request.args.get("next")))


@bp.post("/logout")
def logout():
    if not validate_csrf_token(request.form.get("csrf_token")):
        flash("Invalid session token. Try again.", "error")
        return redirect(url_for("main.home"))
    logout_user()
    flash("Signed out.", "ok")
    return redirect(url_for("main.login"))


@bp.get("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


@bp.get("/servers/<int:server_id>")
@login_required
def server_detail(server_id: int):
    return render_template("server_detail.html", server_id=server_id)


@bp.get("/servers/add")
@login_required
def add_server():
    return render_template("add_server.html")
