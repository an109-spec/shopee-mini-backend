import os
from datetime import timedelta


class BaseConfig:
    ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = False
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")

    # ======================
    # DATABASE
    # ======================
    DB_USER = os.getenv("APP_DB_USER")
    DB_PASSWORD = os.getenv("APP_DB_PASSWORD")
    DB_NAME = os.getenv("APP_DB_NAME")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")

    @classmethod
    def build_db_uri(cls):
        if not all([cls.DB_USER, cls.DB_PASSWORD, cls.DB_NAME]):
            raise RuntimeError("Database environment variables not properly set")

        return (
            f"postgresql+psycopg2://{cls.DB_USER}:{cls.DB_PASSWORD}"
            f"@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
        )

    # Ưu tiên biến môi trường
    SQLALCHEMY_DATABASE_URI = (
        os.getenv("SQLALCHEMY_DATABASE_URI")
        or os.getenv("DATABASE_URL")
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True
    }

    # ======================
    # JWT
    # ======================
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        seconds=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 3600))
    )

    # ======================
    # MAIL
    # ======================
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True") == "True"
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "False") == "True"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")

    # ======================
    # SOCKET.IO
    # ======================
    SOCKETIO_MESSAGE_QUEUE = os.getenv("SOCKETIO_MESSAGE_QUEUE")


class DevelopmentConfig(BaseConfig):
    ENV = "development"
    DEBUG = True
    MAIL_SUPPRESS_SEND = True

    SQLALCHEMY_DATABASE_URI = (
        BaseConfig.SQLALCHEMY_DATABASE_URI
        or "sqlite:///shopee_mini.db"
    )


class ProductionConfig(BaseConfig):
    ENV = "production"
    DEBUG = False

    @classmethod
    def validate(cls):
        if cls.SECRET_KEY == "dev-secret":
            raise RuntimeError("SECRET_KEY must be set in production")


class TestingConfig(BaseConfig):
    ENV = "testing"
    TESTING = True
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    MAIL_SUPPRESS_SEND = True


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}