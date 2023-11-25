
"""User related endpoints."""
from flask import jsonify, request
from models.user import User
from models.role import Role
from models.person import Person
from app import db
from api.v1.views import api_bp
from functools import wraps


from flask import abort
from functools import wraps

admin_role = Role.query.filter_by(name="admin").first()
provider_role = Role.query.filter_by(name="provider").first()

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get the current user
        token = request.headers.get('Authorization')
        current_user = Person.verify_auth_token(token, User)
        if current_user is None:
            abort(401)  # Unauthorized

        # Check if the current user has the 'admin' role
        if 'admin' not in (role.name for role in current_user.roles):
            abort(403)  # Forbidden

        return f(*args, **kwargs)
    return decorated_function


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
    user = User(**data)
    if not user:
        abort(400)
    if "role" in data.keys():
        if data["role"] == "provider":
            user.roles.append(provider_role)
        elif data["role"] == "admin":
            user.roles.append(admin_role)
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
    user = User.query.get(user_id)
    if not user:
        abort(404)
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
@api_bp.route("/users/phone_no/<string:phone_no>", methods=["GET"], strict_slashes=False)
@admin_required
def get_user_by_phone_no(phone_no):
    """Return a user."""
    user = User.query.filter_by(phone_no=phone_no).first()
    if not user:
        abort(404)
    return jsonify(user.to_dict()), 200
