import http
from flask_testing import TestCase
import unittest
from app import create_app


class TestAuth(TestCase):
    admins_phone = "+254700000000"
    admins_passwd = "1Admin234"

    def create_app(self):
        app = create_app()
        self.app = app
        return app

    def test_user_login(self):
        response = self.client.post(
            "/api/v1/login",
            json={"phone_no": self.admins_phone, "password": self.admins_passwd},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.json)
        self.assertIn("refresh_token", response.json)
        self.assertNotEqual(
            response.json["access_token"], response.json["refresh_token"]
        )
        response2 = self.client.post(
            "/api/v1/login", 
            json={"phone_no": "+254700000001", "password": self.admins_passwd},
        )
        self.assertEqual(response2.status_code, 404)
        self.assertEqual(response2.json["message"], "User not found")

    def test_user_logout(self):
        # Assuming you have an endpoint for user logout, e.g., /api/v1/logout
        access_token = self.get_access_token_for_user("user_phone", "password")
        refresh_token = self.get_refresh_token_for_user("user_phone", "password")
        headers = {"Authorization": f"Bearer {access_token}"}
        body = {"refresh_token": refresh_token}
        response = self.client.post("/api/v1/logout", headers=headers, json=body)
        self.assertEqual(response.status_code, 200)

    def test_user_logout1(self):
        # Assuming there is an endpoint for user logout, e.g., /api/v1/logout
        tokens = self.get_user_tokens("user_phone", "password")
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        body = {"refresh_token": refresh_token}
        response = self.client.post("/api/v1/logout", headers=headers, json=body)
        response2 = self.client.post("/api/v1/logout", headers=headers, json={})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response2.status_code, 401)

    def get_access_token_for_user(self, phone_no, password):
        # Helper function to get the access token for a user
        phone_no = self.admins_phone
        password = self.admins_passwd
        response = self.client.post(
            "/api/v1/login", json={"phone_no": phone_no, "password": password}
        )
        return response.json.get("access_token")

    def get_refresh_token_for_user(self, phone_no, password):
        # Helper function to get the refresh token for a user
        phone_no = self.admins_phone
        password = self.admins_passwd
        response = self.client.post(
            "/api/v1/login", json={"phone_no": phone_no, "password": password}
        )
        return response.json.get("refresh_token")

    def get_user_tokens(self, phone_no, password) -> dict:
        # Helper function to get both access and refresh tokens for a user
        phone_no = self.admins_phone
        password = self.admins_passwd
        response = self.client.post(
            "/api/v1/login", json={"phone_no": phone_no, "password": password}
        )
        return {
            "access_token": response.json.get("access_token"),
            "refresh_token": response.json.get("refresh_token"),
        }

    def test_token_refresh(self):
        """Test the refresh of an access token."""
        phone_no = self.admins_phone
        password = self.admins_passwd
        tokens = self.get_user_tokens(phone_no, password)
        refresh_token = tokens["refresh_token"]
        response = self.refresh(tokens)
        self.assertIn("access_token", response.json)
        self.assertNotEqual(response.json["access_token"], refresh_token)
        self.assertNotEqual(response.json["access_token"], tokens["access_token"])

    def refresh(self, tokens) -> http.client.HTTPResponse:
        """Refresh the access token."""
        headers = {"Authorization": f"Bearer {tokens['refresh_token']}"}
        response = self.client.post("/api/v1/refresh", headers=headers)
        return response


if __name__ == "__main__":
    unittest.main()
