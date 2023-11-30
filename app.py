#!/usr/bin/env python3
"""Main entry point for the application."""

from venv import create
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import config.config as config

db = SQLAlchemy()


def create_app():
    """Create an app instance.
    
    :param config_name: The name of the configuration to use.
    :type config_name: Optional[str]
    :return: The created Flask app instance.
    :rtype: Flask
    """

    app = Flask(__name__)

    # set environment
    env = os.environ.get("FLASK_ENV", "default")
    config_class = config.configurations.get(env, config.configurations["default"])
    app.config.from_object(config_class)

    try:
        db.init_app(app)
    except Exception as e:
        print(f"Failed to initialize database: {e}")
        return None

    with app.app_context():
        try:
            from models.person import Person
            from models.user import User
            from models.role import Role
            from models.patient import Patient
            from models.visit import Visit
            from models.encounter import Encounter
            from models.appointment import Appointment

            db.create_all()
        except Exception as e:
            print(f"Failed to create database tables: {e}")
            return None

        # Register blueprints
        try:
            from api.v1.views import api_bp

            app.register_blueprint(api_bp)
        except Exception as e:
            print(f"Failed to register blueprint: {e}")
            return None

        # Register error handlers
        #try:
        ##    from api.v1.views.error_handlers import register_error_handlers

        #    register_error_handlers(api_bp)
        #except Exception as e:
        #    print(f"Failed to register error handlers: {e}")
        #    return None

        # create admin user
        try:
            # create default roles and initial admin user
            from create_init_admin import create_admin
            admin = create_admin(db, User, Role, Person)
            if not admin:
                print("Failed to create admin user.")
                return None
        except Exception as e:
            print(f"Failed to create admin user: {e}")
            return None

    return app

if __name__ == "__main__":
    app = create_app()
    app.run()
