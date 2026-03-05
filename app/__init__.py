import os
from flask import Flask
from datetime import datetime
from app.config import config_by_name
from app.extensions import init_extensions, db
from app.modules.auth import auth_bp
from app.modules.product import product_bp
from app.modules.cart import cart_bp
from app.modules.user import user_bp
from app.modules.order import order_bp
from app.modules.payment import payment_bp
from app.cli import register_cli
from flask_mail import Mail
from flask_migrate import Migrate
mail = Mail()
def create_app():
    app = Flask(__name__)

    # Load environment
    env = os.getenv("FLASK_ENV", "development")
    config_class = config_by_name.get(env)

    if not config_class:
        raise RuntimeError(f"Invalid environment: {env}")

    app.config.from_object(config_class)
    mail.init_app(app)
    # Kiểm tra DB bắt buộc
    if not app.config.get("SQLALCHEMY_DATABASE_URI"):
        raise RuntimeError("Database configuration missing")

    # Init extensions
    init_extensions(app)

    # Dev convenience: auto create SQLite tables
    if env == "development" and app.config["SQLALCHEMY_DATABASE_URI"].startswith("sqlite"):
        with app.app_context():
            from app import models  # noqa
            from app.modules.product import models as product_models
            db.create_all()

    # Register blueprints
    register_blueprints(app)
    register_cli(app)

    @app.context_processor
    def inject_globals():
        return {"current_year": datetime.now().year}

    if app.config["DEBUG"]:
        print("DB URI:", app.config["SQLALCHEMY_DATABASE_URI"])
        print(app.url_map)
    migrate = Migrate(app, db)
    return app


def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(payment_bp)