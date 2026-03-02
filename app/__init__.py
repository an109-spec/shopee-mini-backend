import os
from flask import Flask
from datetime import datetime
from app.config import config_by_name
from app.extensions import init_extensions, db
from app.modules.auth import auth_bp
from app.modules.user import user_bp
from app.cli import register_cli


def create_app():
    app = Flask(__name__)

    # Load environment
    env = os.getenv("FLASK_ENV", "development")
    config_class = config_by_name.get(env)

    if not config_class:
        raise RuntimeError(f"Invalid environment: {env}")

    app.config.from_object(config_class)

    # Validate production
    if env == "production" and hasattr(config_class, "validate"):
        config_class.validate()

    # Build DB URI nếu chưa có
    if not app.config.get("SQLALCHEMY_DATABASE_URI"):
        app.config["SQLALCHEMY_DATABASE_URI"] = config_class.build_db_uri()

    print("ENV =", env)
    print("DATABASE URI =", app.config.get("SQLALCHEMY_DATABASE_URI"))

    # Init extensions
    init_extensions(app)

    # ⚠️ Chỉ auto-create table khi dùng SQLite dev
    if (
        env == "development"
        and str(app.config.get("SQLALCHEMY_DATABASE_URI", "")).startswith("sqlite")
    ):
        with app.app_context():
            from app import models  # đảm bảo model được import
            db.create_all()
            print("SQLite tables created automatically")

    # Register blueprints
    register_blueprints(app)
    register_cli(app)

    @app.context_processor
    def inject_globals():
        return {"current_year": datetime.now().year}

    if app.config.get("DEBUG"):
        print(app.url_map)

    return app


def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)