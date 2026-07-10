import os
import secrets

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv():
        return False


INITIAL_APP_ENV = os.getenv("APP_ENV", "development").lower()

if INITIAL_APP_ENV != "production":
    load_dotenv()


def get_app_env():
    return os.getenv("APP_ENV", INITIAL_APP_ENV).lower()


def normalize_database_url(database_url):
    if database_url and database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql://", 1)
    return database_url


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = normalize_database_url(os.getenv("DATABASE_URL", "sqlite:///urls.db"))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    WTF_CSRF_ENABLED = True
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URI = os.getenv("RATELIMIT_STORAGE_URI", "memory://")
    RATELIMIT_HEADERS_ENABLED = True


class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = os.getenv("SECRET_KEY") or secrets.token_urlsafe(32)


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = normalize_database_url(os.getenv("DATABASE_URL", "sqlite:///:memory:"))
    SECRET_KEY = os.getenv("SECRET_KEY") or secrets.token_urlsafe(32)
    WTF_CSRF_ENABLED = False
    RATELIMIT_ENABLED = False


class ProductionConfig(Config):
    SESSION_COOKIE_SECURE = True
    SECRET_KEY = os.getenv("SECRET_KEY")


CONFIG_BY_ENV = {
    "development": DevelopmentConfig,
    "dev": DevelopmentConfig,
    "testing": TestingConfig,
    "test": TestingConfig,
    "production": ProductionConfig,
    "prod": ProductionConfig,
}


def get_config():
    app_env = get_app_env()
    config_class = CONFIG_BY_ENV.get(app_env, DevelopmentConfig)

    if config_class is ProductionConfig and not config_class.SECRET_KEY:
        raise RuntimeError("SECRET_KEY deve ser definida em ambiente de produção.")

    return config_class
