import os
from datetime import timedelta



class BaseConfig:
    # ======================
    # FLASK
    # ======================
    ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = False
    SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret")

    # ======================
    # DATABASE
    # ======================
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "SQLALCHEMY_DATABASE_URI",
        "sqlite:///shopee_mini.db" #dùng sqlite tránh sập nếu chưa cài postgresql
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True
    }

    # ======================
    # JWT
    # ======================
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        seconds=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 3600))
    )

    # ======================
    # MAIL
    # ======================
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")

    # ======================
    # SOCKET.IO
    # ======================
    SOCKETIO_MESSAGE_QUEUE = os.getenv("SOCKETIO_MESSAGE_QUEUE")


class DevelopmentConfig(BaseConfig):#→ cấu hình riêng cho môi trường DEV
    ENV = "development"
    DEBUG = True
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_SUPPRESS_SEND = True


class ProductionConfig(BaseConfig):
    ENV = "production"
    DEBUG = False
    MAIL_USE_TLS =  False
    MAIL_USE_SSL =  True 


class TestingConfig(BaseConfig):
    ENV = "testing"#Class Attribute không phải phương thức vì k có def
    TESTING = True
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    MAIL_SUPPRESS_SEND = True

#Global Variable (Biến toàn cục)
config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
#bảng ánh xạ 
#giữa tên môi trường và Config class tương ứng
