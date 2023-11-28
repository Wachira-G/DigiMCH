"""Authenticate a person."""

from flask import jsonify, request
from models.user import User
from api.v1.views import api_bp


def authenticate():
    """Authenticate a person."""
    data = request.get_json()
    user = User.query.filter_by(phone_no=data["phone_no"]).first()
    if user and user.check_password(data["password"]):
        return jsonify(user.to_dict()), 200
    else:
        return jsonify({"message": "Invalid credentials."}), 401


@api_bp.route("/login", methods=["POST"], strict_slashes=False)
def login():
    """Login a person."""
    data = request.get_json()
    user = User.query.filter_by(phone_no=data["phone_no"]).first()
    if user and user.check_password(data["password"]):
        token = user.generate_auth_token()
        return jsonify({"token": token}), 200
    else:
        return jsonify({"message": "Invalid credentials."}), 401
