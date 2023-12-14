"""Maternal profile endpoints."""

from flask import request, jsonify
from flask_jwt_extended import jwt_required, decode_token
from marshmallow import ValidationError, schema, fields

from app import db
from api.v1.views import api_bp
from api.v1.views.patient import admin_or_provider_required
from models.maternal_profile import MaternalProfile
from models.patient import Patient


class MaternalProfileSchema(schema.Schema):
    """Maternal profile schema."""
    
    id = fields.Integer(dump_only=True)
    patient_id = fields.Integer(required=False)
    gravida = fields.Integer()
    parity = fields.Integer()
    para = fields.Integer()
    height = fields.Float()
    weight = fields.Float()
    lmp = fields.Date()


# create a patient's maternal profile
@api_bp.route("/patients/<int:patient_id>/maternal_profile", methods=["POST"], strict_slashes=False)
@admin_or_provider_required
@jwt_required()
def create_maternal_profile(patient_id):
    """Create a patient's maternal profile."""
    schema = MaternalProfileSchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    patient = db.session.query(Patient).get(patient_id)
    if not patient:
        return jsonify({"message": "Patient not found."}), 404
    
    try:
        maternal_profile = MaternalProfile(**data)

    except Exception as err:
        return jsonify({"message": f"Failed to create maternal profile: {err}."}), 400

    maternal_profile.patient = patient

    db.session.add(maternal_profile)
    db.session.commit()

    return jsonify({"message": "Maternal profile created successfully."}), 201


# get a patient's maternal profile
@api_bp.route("/patients/<int:patient_id>/maternal_profile", methods=["GET"], strict_slashes=False)
@admin_or_provider_required
@jwt_required()
def get_maternal_profile(patient_id):
    """Get a patient's maternal profile."""
    patient = db.session.query(Patient).get(patient_id)
    if not patient:
        return jsonify({"message": "Patient not found."}), 404

    maternal_profile = patient.maternal_profile
    if not maternal_profile:
        return jsonify({"message": "Maternal profile not found."}), 404

    age = maternal_profile.age
    edd = maternal_profile.edd

    schema = MaternalProfileSchema()
    maternal_profile_dict = schema.dump(maternal_profile)
    maternal_profile_dict['age'] = age if age else None
    maternal_profile_dict['edd'] = edd.isoformat() if edd else None
    return jsonify(maternal_profile_dict), 200

# get a patient's maternal profile (self)
@api_bp.route("/patients/me/maternal_profile", methods=["GET"], strict_slashes=False)
@jwt_required()
def get_maternal_profile_self():
    """Get a patient's maternal profile."""
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"message": "Token not found."}), 404
    if token.startswith('Bearer '):
        token = token.split()[1]

    patient_id = decode_token(encoded_token=token)["sub"]
    if not patient_id:
        return jsonify({"message": "Patient not found."}), 404
    patient = db.session.query(Patient).get(patient_id)
    if not patient:
        return jsonify({"message": "Patient not found."}), 404

    maternal_profile = patient.maternal_profile
    if not maternal_profile:
        return jsonify({"message": "Maternal profile not found."}), 404

    age = maternal_profile.age
    edd = maternal_profile.edd

    schema = MaternalProfileSchema()
    maternal_profile_dict = schema.dump(maternal_profile)
    maternal_profile_dict['age'] = age if age else None
    maternal_profile_dict['edd'] = edd.isoformat() if edd else None
    return jsonify(maternal_profile_dict), 200


# update a patient's maternal profile
@api_bp.route("/patients/<int:patient_id>/maternal_profile", methods=["PUT"], strict_slashes=False)
@admin_or_provider_required
@jwt_required()
def update_maternal_profile(patient_id):
    """Update a patient's maternal profile."""
    schema = MaternalProfileSchema()
    try:
        data = schema.load(request.get_json(), partial=True)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    patient = db.session.query(Patient).get(patient_id)
    if not patient:
        return jsonify({"message": "Patient not found."}), 404
    
    maternal_profile = patient.maternal_profile
    if not maternal_profile:
        return jsonify({"message": "Maternal profile not found."}), 404
    
    for key, value in data.items():
        setattr(maternal_profile, key, value)
    
    db.session.commit()

    return jsonify({"message": "Maternal profile updated successfully."}), 200


# delete a patient's maternal profile
@api_bp.route("/patients/<int:patient_id>/maternal_profile", methods=["DELETE"], strict_slashes=False)
@admin_or_provider_required
@jwt_required()
def delete_maternal_profile(patient_id):
    """Delete a patient's maternal profile."""
    patient = db.session.query(Patient).get(patient_id)
    if not patient:
        return jsonify({"message": "Patient not found."}), 404
    
    maternal_profile = patient.maternal_profile
    if not maternal_profile:
        return jsonify({"message": "Maternal profile not found."}), 404
    
    db.session.delete(maternal_profile)
    db.session.commit()

    return jsonify({"message": "Maternal profile deleted successfully."}), 200
