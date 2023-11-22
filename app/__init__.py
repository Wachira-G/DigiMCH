
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from storage.db_storage import DbStorage
from storage.config import Config

db = SQLAlchemy()

def create_app(config_name="development"):
    """Create an app instance."""
    app = Flask(__name__)
    #app.config.from_object(configurations[config_name])
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        # Register database
        # db = SQLAlchemy(app)
        # storage = DbStorage(db)

        from models.patient import Patient
        db.create_all()

        storage = DbStorage(db)
        app.config['storage'] = storage

        # Register routes and views blueprint
        from api.v1.views import api_bp
        app.register_blueprint(api_bp)

    return app