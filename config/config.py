import os

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "sqlite:///" + os.path.join(basedir, "tmp", "development.db")
    )
    SQLALCHEMY_T = False
    JSONIFY_PRETTYPRRACK_MODIFICATIONSINT_REGULAR = True
    SECRET_KEY = "0WJ090JWJWTG0"


"""
# Define different configurations
class Config:
    SECRET_KEY = 'your_secret_key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///development.db'


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///production.db'


configurations = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}
"""
