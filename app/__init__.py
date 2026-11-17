"""Demo Monitoring Infrastructure — Flask application factory."""

from __future__ import annotations

import os
from typing import Any

from flask import Flask


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    app = Flask(
        __name__,
        instance_relative_config=True,
        template_folder=os.path.join(root, "templates"),
        static_folder=os.path.join(root, "static"),
    )

    os.makedirs(app.instance_path, exist_ok=True)

    # Placeholder for local demo only — never hardcode a production secret.
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-change-me"),
        DATABASE=os.environ.get(
            "DATABASE_PATH",
            os.path.join(app.instance_path, "monitoring.db"),
        ),
        DEMO_PASSWORD=os.environ.get("DEMO_PASSWORD", "admin123"),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=False,  # local HTTP demo only
    )

    if test_config is not None:
        app.config.update(test_config)

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

    return app
