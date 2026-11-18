"""Demo Monitoring Infrastructure — Flask application factory."""

from __future__ import annotations

import logging
import os
from typing import Any

from flask import Flask, render_template


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    app = Flask(
        __name__,
        instance_relative_config=True,
        template_folder=os.path.join(root, "templates"),
        static_folder=os.path.join(root, "static"),
    )

    os.makedirs(app.instance_path, exist_ok=True)

    flask_env = os.environ.get("FLASK_ENV", "development")
    secret = os.environ.get("SECRET_KEY")
    if flask_env == "production" and not secret:
        raise RuntimeError("SECRET_KEY must be set when FLASK_ENV=production")

    # Local demo default only — override via env; never use as a production secret.
    app.config.from_mapping(
        SECRET_KEY=secret or "dev-only-change-me",
        DATABASE=os.environ.get(
            "DATABASE_PATH",
            os.path.join(app.instance_path, "monitoring.db"),
        ),
        DEMO_PASSWORD=os.environ.get("DEMO_PASSWORD", "admin123"),
        SKIP_SSH=os.environ.get("SKIP_SSH", "").lower() in ("1", "true", "yes"),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=False,  # local HTTP demo only
    )

    if test_config is not None:
        app.config.update(test_config)

    logging.basicConfig(level=logging.INFO)

    from app import db
    from app.routes import bp
    from app.seed import seed_admin_user

    db.init_app(app)
    app.register_blueprint(bp)

    with app.app_context():
        db.init_db()
        seed_admin_user(app)

    @app.context_processor
    def inject_auth() -> dict[str, Any]:
        from app.auth import get_csrf_token, is_authenticated

        return {
            "is_authenticated": is_authenticated(),
            "csrf_token": get_csrf_token,
        }

    @app.errorhandler(404)
    def not_found(_e: Exception):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e: Exception):
        app.logger.exception("Internal error: %s", type(e).__name__)
        return render_template("errors/500.html"), 500

    return app
