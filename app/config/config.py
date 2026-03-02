import os
from datetime import timedelta


class BaseConfig:
    # ======================
    # FLASK
    # ======================
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

    # Ưu tiên DATABASE_URL / SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_DATABASE_URI = (
        os.getenv("SQLALCHEMY_DATABASE_URI")
        or os.getenv("DATABASE_URL")
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True
    }

    @classmethod
    def build_db_uri(cls):
        if not all([cls.DB_USER, cls.DB_PASSWORD, cls.DB_NAME]):
            raise RuntimeError(
                "Database environment variables not properly set "
                "(APP_DB_USER, APP_DB_PASSWORD, APP_DB_NAME)"
            )

        return (
            f"postgresql+psycopg2://{cls.DB_USER}:{cls.DB_PASSWORD}"
            f"@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
        )


class DevelopmentConfig(BaseConfig):
    ENV = "development"
    DEBUG = True
    MAIL_SUPPRESS_SEND = True


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