import os 
from flask import Flask
from app.config import config_by_name
from app.extensions import init_extensions
from app.modules.auth import auth_bp


def create_app():
    app = Flask(__name__)
    # Load config theo môi trường
    env = os.getenv("FLASK_ENV", "development")
    config_class=config_by_name.get(env)
    if not config_class:
       raise RuntimeError(f"Invalid environment: {env}")
    
    app.config.from_object(config_class)
    # Init extensions
    init_extensions(app)
    # Register blueprints (để trống trước, thêm dần sau)
    register_blueprints(app)


    return app
    print(app.url_map)


def register_blueprints(app):
    # Khi chưa có module thì để trống
    app.register_blueprint(auth_bp)













