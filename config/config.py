import os

# from dot-env import load_dotenv

# load_dotenv()

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

posgres_username = os.environ.get("POSTGRES_USERNAME")
posgres_password = os.environ.get("POSTGRES_PASSWORD")
posgres_database = os.environ.get("POSTGRES_DATABASE")
posgres_host = os.environ.get("POSTGRES_HOST")
posgres_port = os.environ.get("POSTGRES_PORT")

postgresdb_config = f"postgresql://{posgres_username}:{posgres_password}@{posgres_host}:{posgres_port}/{posgres_database}"


class Config(object):
    DEBUG = False
    TESTING = False
    CRSF_ENABLED = True
    SQLALCHEMY_T = False
    JSONIFY_PRETTYPRRACK_MODIFICATIONSINT_REGULAR = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "sqlite:///" + os.path.join(basedir, "tmp", "development.db")
    )
    SECRET_KEY = "0WJ090JWJWTG0"
    JWT_SECRET_KEY = "0WJ090JWJWTG090E0JWJW"
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ["access", "refresh"]
    JWT_ACCESS_TOKEN_EXPIRES = 60 * 60 * 24
    JWT_REFRESH_TOKEN_EXPIRES = 60 * 60 * 24 * 30
    # JWT_TOKEN_LOCATION = ["headers", "cookies"]
    # JWT_COOKIE_SECURE = False
    # JWT_COOKIE_CSRF_PROTECT = False
    # JWT_CSRF_CHECK_FORM = False
    # JWT_COOKIE_DOMAIN = "localhost"


class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"  # use in-memory SQLite for testing
    TESTING = True


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = postgresdb_config


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


# heroku related config
class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


configurations = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestConfig,
    "staging": StagingConfig,
    "default": DevelopmentConfig,
}
