#!/usr/bin/env python3
"""Main entry point for the application."""

from venv import create
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config.config import Config, TestConfig
from typing import Optional

db = SQLAlchemy()


def create_app(config_name: Optional[str] = "development", testing: bool = False):
    """Create an app instance.
    
    :param config_name: The name of the configuration to use.
    :type config_name: Optional[str]
    :return: The created Flask app instance.
    :rtype: Flask
    """

    app = Flask(__name__)
    if testing:
        app.config.from_object(TestConfig)
    else:
        app.config.from_object(Config)

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
        try:
            from api.v1.views.error_handlers import register_error_handlers

            register_error_handlers(app)
        except Exception as e:
            print(f"Failed to register error handlers: {e}")
            return None

        # create admin user
        try:
            admin = create_admin(db, User, Role, Person)
            if not admin:
                print("Failed to create admin user.")
                return None
        except Exception as e:
            print(f"Failed to create admin user: {e}")
            return None

    return app


def create_admin(db, User, Role, Person):
    """Create an admin user."""

    # create roles
    # admin
    try:
        admin_role = Role.query.filter_by(name="admin").first()
        if admin_role:
            pass
        else:
            admin_role = Role(name="admin", description="root Administrator")
            db.session.add(admin_role)
            db.session.commit()
    except Exception as e:
        print(f"Failed to create admin role: {e}")
        return None

    # provider
    try:
        provider_role = Role.query.filter_by(name="provider").first()
        if provider_role:
            pass
        else:
            provider_role = Role(name="provider")
            db.session.add(provider_role)
            db.session.commit()
    except Exception as e:
        print(f"Failed to create provider role: {e}")
        return None

    # patient
    try:
        patient_role = Role.query.filter_by(name="patient").first()
        if patient_role:
            pass
        else:
            patient_role = Role(name="patient")
            db.session.add(patient_role)
            db.session.commit()
    except Exception as e:
        print(f"Failed to create patient role: {e}")
        return None

    # create initial admin user
    try:
        admin = User.query.filter_by(phone_no="254700000000").first()
        if admin:
            return admin
        admin = User(
            first_name="Admin",
            surname="Admin",
            phone_no="254700000000",
            middle_name="Admin",
            password_hash=Person.generate_hash("admin"),
            sex="admin",
            birth_date="2023-01-01T00:00:00.000000",
            facility_id="1",
        )
        admin.roles.append(admin_role)
        db.session.add(admin)
        db.session.commit()
        return admin
    except Exception as e:
        print(f"Failed to create admin user: {e}")
        return None


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
