
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from storage.db_storage import DbStorage
from storage.config import Config
from typing import Optional

db = SQLAlchemy()

def create_app(config_name: Optional[str] = "development"):
    """Create an app instance.
    
    :param config_name: The name of the configuration to use.
    :type config_name: Optional[str]
    :return: The created Flask app instance.
    :rtype: Flask
    """

    app = Flask(__name__)
    #app.config.from_object(configurations[config_name])
    app.config.from_object(Config)

    try:
        db.init_app(app)
    except Exception as e:
        print(f"Failed to initialize database: {e}")
        return None

    with app.app_context():
        try:
            from models.patient import Patient
            from models.provider import Provider
            db.create_all()
        except Exception as e:
            print(f"Failed to create database tables: {e}")
            return None

        try:
            storage = DbStorage(db)
            app.config['storage'] = storage
        except Exception as e:
            print(f"Failed to initialize storage engine: {e}")
            return None

        # Register routes and views blueprint
        try:
            from api.v1.views import api_bp
            app.register_blueprint(api_bp)
        except Exception as e:
            print(f"Failed to register blueprint: {e}")
            return None
    return app