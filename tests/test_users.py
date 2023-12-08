"""Module for testing users."""

import unittest
from urllib import response
from flask import json
from app import create_app, db
from models.user import User
from models.role import Role


class TestUser(unittest.TestCase):
    def create_app(self):
        app = create_app()
        self.app = app
        return app

    def setUp(self):
        self.app = self.create_app()
        self.client = self.app.test_client
        self.user_data = {
            "first_name": "Test_user",
            "surname": "doe",
            "phone_no": "+254704567890",
            "role": "admin",
            "sex": "female",
            "password": "123password",
            "birth_date": "2002-11-29T00:00:00",
            "facility_id": "2",
        }
        self.current_user_tokens = self.client().post(
            "/api/v1/login", json={"phone_no": "+254700000000", "password": "1Admin234"}
        )
        self.auth_header = {
            "Authorization": f'Bearer {self.current_user_tokens.json["access_token"]}'
        }

        with self.app.app_context():
            db.create_all()

    def test_user_creation(self):
        res = self.client().post(
            "/api/v1/users", json=self.user_data, headers=self.auth_header
        )
        self.assertEqual(res.status_code, 201)
        self.assertIn("first_name", str(res.data))
        self.assertTrue(res.json["first_name"] == "Test_user")
        self.assertTrue(res.json["roles"][0]["name"] == self.user_data["role"])
        self.assertTrue(res.json["__class__"] == "User")

    def test_user_update(self):
        """Test API can update an existing user. (PUT request)"""
        res = self.client().put(
            "/api/v1/users/1",
            json={"middle_name": "Test_user_updated"},
            headers=self.auth_header,
        )
        self.assertEqual(res.status_code, 201)
        res = self.client().put(
            "/api/v1/users/1",
            json={"first_name": "Test_user_updated"},
            headers=self.auth_header,
        )
        self.assertEqual(res.status_code, 201)
        self.assertIn("Test_user_updated", str(res.data))

    def test_user_update_self(self):
        """Test API can update an existing user. (PUT request)"""
        res = self.client().put(
            "/api/v1/users/me",
            json={"middle_name": "Test_user_updated"},
            headers=self.auth_header,
        )
        self.assertEqual(res.status_code, 201)
        res = self.client().put(
            "/api/v1/users/me",
            json={"first_name": "Test_user_updated"},
            headers=self.auth_header,
        )
        self.assertEqual(res.status_code, 201)
        self.assertIn("Test_user_updated", str(res.data))

    def test_user_deletion(self):
        """Test API can delete an existing user. (DELETE request)."""
        with self.app.app_context():
            # create user
            res = self.client().post(
                "/api/v1/users", json=self.user_data, headers=self.auth_header
            )
            if res.status_code == 201:
                user = res.json["id"]
                user_to_delete = db.session.get(User, user)
                db.session.add(user_to_delete)
                db.session.commit()
                res = self.client().delete(
                    f"/api/v1/users/{user_to_delete.id}", headers=self.auth_header
                )
                self.assertEqual(res.status_code, 204)
                self.assertEqual(db.session.get(User, user_to_delete.id), None)
            res = self.client().delete(f"/api/v1/users/{40}", headers=self.auth_header)
            self.assertEqual(res.status_code, 404)

    def test_get_users(self):
        """Test API can get all users. (GET request)."""
        res = self.client().get("/api/v1/users", headers=self.auth_header)
        self.assertEqual(res.status_code, 200)
        self.assertIn("first_name", str(res.data))
        self.assertTrue(res.json[0]["first_name"] == "Root Admin")
        self.assertTrue(len(res.json) == 1)

    def test_get_user_by_id(self):
        """Test API can get a single user by using it's id."""
        res = self.client().get("/api/v1/users/1", headers=self.auth_header)
        self.assertEqual(res.status_code, 200)
        self.assertIn("Root Admin", str(res.data))
        self.assertTrue(res.json["first_name"] == "Root Admin")
        res = self.client().get("api/v1/user/40", headers=self.auth_header)
        self.assertEqual(res.status_code, 404)

    def test_get_user_by_phone(self):
        """Test API can get a single user by using it's phone number."""
        res = self.client().get(
            "/api/v1/users/phone_no/+254700000000", headers=self.auth_header
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn("Root Admin", str(res.data))
        self.assertTrue(res.json["first_name"] == "Root Admin")
        res = self.client().get(
            "api/v1/user/phone/+254700347287", headers=self.auth_header
        )
        self.assertTrue(res.status_code, 404)

    def test_provider_cannot_create_admin(self):
        """Test provider user cannot create admin user."""
        pass

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()


if __name__ == "__main__":
    unittest.main()
