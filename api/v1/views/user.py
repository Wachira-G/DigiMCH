"""User related endpoints."""

from flask import jsonify, request, abort, current_app
from functools import wraps

from flask_jwt_extended import get_jwt_identity, jwt_required, decode_token
from app import db
from api.v1.views import api_bp
from models.person import Person
from models.role import Role
from models.user import User


admin_role = db.session.query(Role).filter_by(name="admin").first()
provider_role = db.session.query(Role).filter_by(name="provider").first()
patient_role = db.session.query(Role).filter_by(name="patient").first()


def admin_required(f):
    """Restrict access to admin users."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get the auth token
        token = request.headers.get("Authorization")
        if token.startswith("Bearer "): # strip the bearer prefix
                token = token[7:]

        if not token:
            return jsonify({"message": "Token is missing"}), 401

        current_user_id = decode_token(encoded_token=token)['sub']

        # Get the current user
        if current_user_id is None:
            return(
                jsonify(
                    {"message": "Authentication is required to access this resource"}
                ), 
                401
            )
        current_user = db.session.get(User, current_user_id)
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

def get_role(name):
    """Return a role by name - helper function."""
    if name:
        name = name.lower()
    role = db.session.query(Role).filter_by(name=name).first()
    return role

# get all users
@api_bp.route("/users", methods=["GET"], strict_slashes=False, endpoint='get_users')
@admin_required
@jwt_required()
def get_users():
    """Return all users."""
    users = db.session.query(User).all()
    return jsonify([user.to_dict() for user in users]), 200


# create a user
@api_bp.route("/users", methods=["POST"], strict_slashes=False, endpoint='create_user')
@admin_required
@jwt_required()
def create_user():
    """Create a user."""
    data = request.get_json()
    if not data:
        abort(400, 'Invalid data')

    roles = []
    if "role" in data:
        role = get_role(data["role"])
        if not role:
            abort(400, f'Invalid role: {data["role"]}')
        roles.append(role)
        del data["role"]

    if "roles" in data:
        for role_name in data["roles"]:
            role = get_role(role_name)
            if not role:
                abort(400, f'Invalid role: {role_name}')
            roles.append(role)
        del data["roles"]

    user = User(**data)
    if not user:
        abort(400, 'Failed to create user')
    user.roles.extend(roles)

    db.session.add(user)
    db.session.commit()

    # TODO send code to user's phone number to use as login and prompt sett passowrd
    return jsonify(user.to_dict()), 201

# update a user
# TODO what happens if current user wants to update self, and is not admin?
@api_bp.route("/users/<string:user_id>", methods=["PUT"], strict_slashes=False)
@admin_required
@jwt_required()
def update_user(user_id):
    """Update a user."""
    data = request.get_json()
    if not data:
        abort(400, 'Invalid data')

    user = db.session.get(User, user_id)
    if not user:
        abort(404, "User not found")

    if "role" in data:
        role = user.get_role(data["role"].lower())
        if role is None:
            abort(400, f'Invalid role: {data["role"]}')
        user.assign_role(role)
        del data["role"]

    if "roles" in data:
        for role in data["roles"]:
            role = user.get_role(role)
            if role is None:
                abort(400, f'Invalid role: {role}')
            user.assign_role(role)
        del data["roles"]

    if "remove_role" in data:
        role = db.session.query(Role).filter_by(name=data["remove_role"].lower()).first()
        if role:
            user.remove_role(role)
        else:
            abort(400, f'Invalid role: {data["remove_role"]}')
        del data["remove_role"]

    user.update(**data)
    return jsonify(user.to_dict()), 201

@api_bp.route("/users/me", methods=["PUT"], strict_slashes=False)
@jwt_required()
def update_current_user():
    """Update the current user."""
    data = request.get_json()
    if not data:
        abort(400, 'Invalid data')

    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"message": "Token is missing"}), 401
    # Get the current user
    current_user = db.session.get(User, get_jwt_identity())
    if current_user is None:
        return (
            jsonify(
                {"message": "Authentication is required to access this resource"}
            ),
            401,
        )

    if "role" in data:
        user_has_role = current_user.get_role(data["role"].lower())
        if user_has_role:
            del data["role"]
        else:
            role = get_role(data["role"])
            if not role:
                abort(400, f'Invalid role: {data["role"]}')
            current_user.assign_role(role)
            del data["role"]


    if "roles" in data:
        for role_name in data["roles"]:
            role = get_role(role_name)
            if not role:
                abort(400, f'Invalid role: {role_name}')
            if role in current_user.roles:
                continue
            current_user.assign_role(role)
        del data["roles"]

    if "remove_role" in data:
        role = db.session.query(Role).filter_by(name=data["remove_role"].lower()).first()
        if role:
            current_user.remove_role(role)
        else:
            abort(400, f'Invalid role: {data["remove_role"]}')
        del data["remove_role"]

    current_user.update(**data)
    return jsonify(current_user.to_dict()), 201


# delete a user
@api_bp.route("/users/<string:user_id>", methods=["DELETE"], strict_slashes=False)
@admin_required
@jwt_required()
def delete_user(user_id):
    """Delete a user."""
    user = db.session.get(User, user_id)
    if not user:
        abort(404, "User not found")
    db.session.delete(user)
    db.session.commit()
    return jsonify({}), 204


# get a user by id
@api_bp.route("/users/<string:user_id>", methods=["GET"], strict_slashes=False)
@admin_required
@jwt_required()
def get_user(user_id):
    """Return a user."""
    user = db.session.get(User, user_id)
    if not user:
        abort(404, "User not found")
    return jsonify(user.to_dict()), 200


# get a user by phone_no
@api_bp.route(
    "/users/phone_no/<string:phone_no>", methods=["GET"], strict_slashes=False
)
@admin_required
@jwt_required()
def get_user_by_phone_no(phone_no):
    """Return a user."""
    user = db.session.query(User).filter_by(phone_no=phone_no).first()
    if not user:
        abort(404, "User not found")
    return jsonify(user.to_dict()), 200
