
"""Role related endpoints."""

from flask import jsonify, request, abort
from api.v1.views import api_bp
from app import db
from models.role import Role


@api_bp.route("/roles", methods=["GET"], strict_slashes=False)
def get_roles():
    """Return all roles."""
    roles = Role.query.all()
    return jsonify([role.to_dict() for role in roles]), 200

@api_bp.route("/roles", methods=["POST"], strict_slashes=False)
def create_role():
    """Create a role."""
    data = request.get_json()
    role = Role(name=data["name"])
    db.session.add(role)
    db.session.commit()
    return jsonify(role.to_dict()), 201

@api_bp.route("/roles/<role_id>", methods=["PUT"], strict_slashes=False)
def update_role(role_id):
    """Update a role."""
    data = request.get_json()
    role = db.session.query(Role).get(role_id)
    if role:
        role.name = data["name"]
        db.session.commit()
        return jsonify(role.to_dict()), 200
    else:
        abort(404)

@api_bp.route("/roles/<role_id>", methods=["DELETE"], strict_slashes=False)
def delete_role(role_id):
    """Delete a role."""
    role = db.session.query(Role).get(role_id)
    if role:
        db.session.delete(role)
        db.session.commit()
        return jsonify({"message": "Role deleted successfully."}), 200
    else:
        abort(404)

@api_bp.route("/roles/<role_id>", methods=["GET"], strict_slashes=False)
def get_role(role_id):
    """Get a role by id."""
    role = db.session.query(Role).get(role_id)
    if role:
        return jsonify(role.to_dict()), 200
    else:
        return abort(404)

@api_bp.route("/roles/name/<name>", methods=["GET"], strict_slashes=False)
def get_role_by_name(name):
    """Get a role by name."""
    role = db.session.query(Role).filter_by(name=name).first()
    if role:
        return jsonify(role.to_dict()), 200
    else:
        return abort(404)