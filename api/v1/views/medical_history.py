"""Module for medical history endpoints."""

from flask import jsonify, request, abort
from flask_jwt_extended import jwt_required, decode_token
from marshmallow import Schema, fields, ValidationError
from api.v1.views import api_bp
from api.v1.views.patient import admin_required, admin_or_provider_required
from app import db
from models.medical_history import MedicalHistory
from models.patient import Patient
from models.user import User


class MedicalHistorySchema(Schema):
    surgical_operation = fields.Str()
    diabetes = fields.Bool()
    hypertension = fields.Bool()
    blood_transfusion = fields.Bool()
    tuberculosis = fields.Bool()
    drug_allergy = fields.Bool()
    drug_allergy_details = fields.Str()
    other_allergies = fields.Str()
    family_history_twins = fields.Bool()
    family_history_tuberculosis = fields.Bool()


# create a patient's medical history
@api_bp.route(
    "/patients/<int:patient_id>/medical-history", methods=["POST"], strict_slashes=False
)
@admin_or_provider_required
@jwt_required()
def create_medical_history(patient_id):
    """Create a patient's medical history."""

    schema = MedicalHistorySchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"message": "Invalid input data", "errors": err.messages}), 400

    patient = db.session.query(Patient).get(patient_id)
    if not patient:
        return jsonify({"message": "Patient not found"}), 404

    medical_history = MedicalHistory(**data)
    medical_history.patient = patient
    db.session.add(medical_history)
    db.session.commit()

    return (
        jsonify(
            {
                "message": f"Medical History for patient id {patient.id} created successfully"
            }
        ),
        201,
    )


# get a patient's medical history
@api_bp.route(
    "/patients/<int:patient_id>/medical-history", methods=["GET"], strict_slashes=False
)
@admin_or_provider_required
@jwt_required()
def get_medical_history(patient_id):
    """Get a patient's medical history."""

    patient = db.session.query(Patient).get(patient_id)
    if not patient:
        return jsonify({"message": "Patient not found"}), 404

    medical_history = patient.medical_history
    if not medical_history:
        return jsonify({"message": "Medical history not found"}), 404

    return jsonify(medical_history.to_dict()), 200


# get a patient's medical history (self)
@api_bp.route("/patients/me/medical-history", methods=["GET"], strict_slashes=False)
@jwt_required()
def get_medical_history_self():
    """Get a patient's medical history."""

    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"message": "Missing authorization header"}), 401

    token = token.split(" ")[1]
    patient_id = decode_token(token)["sub"]
    patient = db.session.query(Patient).get(patient_id)
    if not patient:
        return jsonify({"message": "User not found"}), 404

    medical_history = patient.medical_history
    if not medical_history:
        return jsonify({"message": "Medical history not found"}), 404

    return jsonify(medical_history.to_dict()), 200


# update a patient's medical history
@api_bp.route(
    "/patients/<int:patient_id>/medical-history", methods=["PUT"], strict_slashes=False
)
@admin_or_provider_required
@jwt_required()
def update_medical_history(patient_id):
    """Update a patient's medical history."""
    schema = MedicalHistorySchema()
    try:
        data = schema.load(request.get_json(), partial=True)
    except ValidationError as err:
        return jsonify({"message": "Invalid input data", "erors": err.messages}), 400

    patient = db.session.query(Patient).get(patient_id),
    if not patient:
        return jsonify({"message": "Patient not found"}), 404

    medical_history = patient.medical_history
    if not medical_history:
        return jsonify({"message": "Medical history not found"}), 404

    medical_history.update(data)
    return jsonify({"message": "Medical history updated successfully"}), 200


# delete a patient's medical history
@api_bp.route(
    "/patients/<int:patient_id>/medical-history",
    methods=["DELETE"],
    strict_slashes=False,
)
@admin_or_provider_required
@jwt_required()
def delete_medical_history(patient_id):
    """Delete a patient's medical history."""
    patient = db.session.query(Patient).get(patient_id)
    if not patient:
        return jsonify({"message": "Patient not found"}), 404

    medical_history = patient.medical_history
    if not medical_history:
        return jsonify({"message": "Medical history not found"}), 404

    db.session.delete(medical_history)
    db.session.commit()

    return (
        jsonify(
            {
                "message": f"Medical history for patient id: {patient.id} deleted successfully."
            }
        ),
        200,
    )
