"""App routes: auth, inventory, dashboard, and read-only metrics."""

from __future__ import annotations

from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from app.auth import (
    login_required,
    login_user,
    logout_user,
    validate_csrf_token,
    verify_password,
)
from app.db import query_one
from app.metrics import format_bytes
from app.servers import (
    check_new_server_reachable,
    create_server,
    dashboard_rows,
    fetch_metrics_for,
    get_server,
)
from app.validators import parse_server_form

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
    servers = dashboard_rows()
    return render_template(
        "dashboard.html",
        servers=servers,
        refresh_seconds=10,
    )


@bp.route("/servers/add", methods=["GET", "POST"])
@login_required
def add_server():
    if request.method == "GET":
        return render_template("add_server.html")

    if not validate_csrf_token(request.form.get("csrf_token")):
        flash("Invalid session token. Try again.", "error")
        return render_template("add_server.html"), 400

    try:
        data = parse_server_form(request.form)
    except ValueError as exc:
        flash(str(exc), "error")
        return render_template("add_server.html"), 400

    if not check_new_server_reachable(data):
        flash(
            "Unreachable or auth failed — check host, port, and credentials.",
            "error",
        )
        return render_template("add_server.html"), 400

    server_id = create_server(data)
    flash("Server added.", "ok")
    return redirect(url_for("main.server_detail", server_id=server_id))


@bp.get("/servers/<int:server_id>")
@login_required
def server_detail(server_id: int):
    server = get_server(server_id)
    if server is None:
        abort(404)
    metrics = fetch_metrics_for(server_id)
    status = "reachable" if metrics is not None else "unreachable"
    return render_template(
        "server_detail.html",
        server=server,
        metrics=metrics,
        status=status,
        format_bytes=format_bytes,
        refresh_seconds=10,
    )
