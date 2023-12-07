from flask import Flask
from flask_testing import TestCase
from sqlalchemy import inspect
import unittest
from app import create_app, db


class TestApp(TestCase):
    def create_app(self):
        app = create_app()
        self.app = app
        return app

    def test_status(self):
        response = self.client.get("/api/v1/status")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "OK")

    def test_invalid_endpoint(self):
        response = self.client.get("/invalid_endpoint")
        self.assertEqual(response.status_code, 404)

    def test_database_initialization(self):
        # Ensure necessary tables are created
        with self.app.app_context():
            from models.person import Person
            from models.user import User
            from models.role import Role
            from auth.blocklist import TokenBlockList

            # TODO
            # visit, appointment, encounter, location, patient, patient_history

            all_models = [Person, User, Role, TokenBlockList]
            # Patient, Visit, Appointment, Encounter, Location,
            # patient_history

            inspector = inspect(db.engine)
            all_db_tables = inspector.get_table_names()

            for model in all_models:
                table_name = model.__table__.name
                self.assertIn(table_name, all_db_tables)

    def test_jwt_initialization(self):
        # Ensure JWT initialization is successful
        self.assertTrue(self.app.extensions.get("flask-jwt-extended"))

    def test_blueprint_registration(self):
        # Ensure API and auth blueprints are registered
        self.assertIn("api_bp", self.app.blueprints)
        self.assertIn("auth_bp", self.app.blueprints)

    def test_token_blocklist_loader(self):
        # Ensure token_in_blocklist_loader is registered
        self.assertTrue(
            self.app.extensions.get("flask-jwt-extended").token_in_blocklist_loader
        )

    def test_admin_user_creation(self):
        # Ensure the admin user is created successfully
        with self.app.app_context():
            from models.user import User

            admin_user = User.query.filter_by(first_name="Root Admin").first()
            self.assertIsNotNone(admin_user)


if __name__ == "__main__":
    unittest.main()
