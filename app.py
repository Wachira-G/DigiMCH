#!/usr/bin/env python3
"""Main entry point for the application."""

from flask import Flask
from flask_jwt_extended import JWTManager
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
import os
import logging
import config.config as config

db = SQLAlchemy()
jwt_manager = JWTManager()
login_manager = LoginManager()  # TODO wont need this if using JWT


@login_manager.user_loader
def load_user(user_id):
    """Load a user."""
    from models.user import User
    return User.query.get(user_id)


def create_app(*args, **kwargs):
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

    # Initialize extensions
    # Database
    try:
        db.init_app(app)
    except Exception as e:
        logging.error(f"Failed to initialize database: {e}")
        raise

    # JWT - JSON Web Tokens
    try:
        jwt_manager.init_app(app)
    except Exception as e:
        logging.error(f"Failed to initialize JWT: {e}")
        raise

    # Login Manager
    try:
        login_manager.init_app(app)  # TODO wont need this if using JWT
    except Exception as e:
        logging.error(f"Failed to initialize login manager: {e}")
        raise

    # Create database tables and register blueprints and error handlers in app context
    with app.app_context():
        try:
            from auth.blocklist import TokenBlockList
            from models.person import Person
            from models.user import User
            from models.role import Role
            from models.patient import Patient
            from models.visit import Visit
            from models.encounter import Encounter
            from models.appointment import Appointment

            db.create_all()
        except Exception as e:
            logging.error(f"Failed to create database tables: {e}")
            raise

        # Register blueprints
        try:
            from api.v1.views import api_bp
            from auth.auth import auth_bp

            app.register_blueprint(api_bp)
            app.register_blueprint(auth_bp)
        except Exception as e:
            logging.error(f"Failed to register blueprint: {e}")
            raise

        # Register jwt token_in_blocklist_loader
        try:

            @jwt_manager.token_in_blocklist_loader
            def check_if_token_in_blocklist(jwt_header, decrypted_token):
                jti = decrypted_token["jti"]
                return TokenBlockList.is_jti_blocklisted(jti)

        except Exception as e:
            logging.error(f"Failed to load jwt token_in_blocklist_loader: {e}")
            raise

        # Register error handlers
        # try:
        ##    from api.v1.views.error_handlers import register_error_handlers

        #    register_error_handlers(api_bp)
        # except Exception as e:
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
            logging.error(f"Failed to create admin user: {e}")
            return "Failed to create admin user.", 500

    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
