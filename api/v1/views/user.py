"""User related endpoints."""

from flask import jsonify, request, abort
from functools import wraps
from app import db
from api.v1.views import api_bp
from models.person import Person
from models.role import Role
from models.user import User
from api.v1.views.role import create_role


admin_role = Role.query.filter_by(name="admin").first()
provider_role = Role.query.filter_by(name="provider").first()
patient_role = Role.query.filter_by(name="patient").first()


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get the auth token
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"message": "Token is missing"}), 401
        # Get the current user
        current_user = Person.verify_auth_token(token, User)
        if current_user is None:
            return (
                jsonify(
                    {"message": "Authentication is required to access this resource"}
                ),
                401,
            )

        # Check if the current user has the 'admin' role
        if "admin" not in (role.name for role in current_user.roles):
            return (
                jsonify(
                    {"message": "Admin privileges are required to access this resource"}
                ),
                403,
            )

        return f(*args, **kwargs)

    return decorated_function

def create_role(name):
    role = Role.query.filter_by(name=name).first()
    if role is None:
        role = Role(name=name.lower())
        db.session.add(role)
    return role

# get all users
@api_bp.route("/users", methods=["GET"], strict_slashes=False)
@admin_required
def get_users():
    """Return all users."""
    users = db.session.query(User).all()
    return jsonify([user.to_dict() for user in users]), 200


# create a user
@api_bp.route("/users", methods=["POST"], strict_slashes=False)
@admin_required
def create_user():
    """Create a user."""
    data = request.get_json()
    if not data:
        abort(400, 'Invalid data')

    roles = []
    if "role" in data:
        roles.append(create_role(data["role"]))
        del data["role"]

    if "roles" in data:
        for role_name in data["roles"]:
            roles.append(create_role(role_name))
        del data["roles"]

    user = User(**data)
    if not user:
        abort(400, 'Failed to create user')
    user.roles.extend(roles)

    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201

# update a user
# TODO what happens if current user wants to update self, and is not admin?
@api_bp.route("/users/<string:user_id>", methods=["PUT"], strict_slashes=False)
@admin_required
def update_user(user_id):
    """Update a user."""
    data = request.get_json()
    if not data:
        abort(400, 'Invalid data')

    user = User.query.get(user_id)
    if not user:
        abort(404)

    if "role" in data:
        role = user.get_role(data["role"].lower())
        if role is None:
            role = create_role(data["role"].lower())
        user.assign_role(role)
        del data["role"]

    if "roles" in data:
        for role in data["roles"]:
            role = user.get_role(role)
            if role is None:
                role = create_role(role)
            user.assign_role(role)
        del data["roles"]

    if "remove_role" in data:
        role = Role.query.filter_by(name=data["remove_role"].lower()).first()
        if role:
            user.remove_role(role)
        del data["remove_role"]

    user.update(**data)
    return jsonify(user.to_dict()), 200


# delete a user
@api_bp.route("/users/<string:user_id>", methods=["DELETE"], strict_slashes=False)
@admin_required
def delete_user(user_id):
    """Delete a user."""
    user = User.query.get(user_id)
    if not user:
        abort(404)
    db.session.delete(user)
    db.session.commit()
    return jsonify({}), 204


# get a user by id
@api_bp.route("/users/<string:user_id>", methods=["GET"], strict_slashes=False)
@admin_required
def get_user(user_id):
    """Return a user."""
    user = User.query.get(user_id)
    if not user:
        abort(404)
    return jsonify(user.to_dict()), 200


# get a user by phone_no
@api_bp.route(
    "/users/phone_no/<string:phone_no>", methods=["GET"], strict_slashes=False
)
@admin_required
def get_user_by_phone_no(phone_no):
    """Return a user."""
    user = User.query.filter_by(phone_no=phone_no).first()
    if not user:
        abort(404)
    return jsonify(user.to_dict()), 200
