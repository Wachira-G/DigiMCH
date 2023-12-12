"""Module for the PregnancyHistory class's endpoints."""

from flask import jsonify, request, abort
from flask_jwt_extended import jwt_required, decode_token
from marshmallow import Schema, fields, ValidationError
from api.v1.views import api_bp
from api.v1.views.patient import admin_required, admin_or_provider_required
from app import db
from models.pregnancy_history import PregnancyHistory
from models.patient import Patient


class PregnancyHistorySchema(Schema):
    pregnancy_order = fields.Int(required=True)
    year = fields.Int(required=True)
    number_of_anc_attended = fields.Int()
    place_of_childbirth = fields.Str()
    gestation_in_weeks = fields.Int()
    duration_of_labour_hours = fields.Int()
    mode_of_delivery = fields.Str()
    birth_weight_grams = fields.Int()
    sex = fields.Str()
    outcome = fields.Str()
    puerperium = fields.Str()


# create a patient's pregnancy history
@api_bp.route(
        '/patients/<int:patient_id>/pregnancy-history', methods=['POST'], strict_slashes=False
)
@admin_or_provider_required
@jwt_required()
def create_pregnancy_history(patient_id):
    """Create a patient's pregnancy history."""

    schema = PregnancyHistorySchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"message": "Invalid input data", "errors": err.messages}), 400

    patient = db.session.query(Patient).get(patient_id)
    if not patient:
        return jsonify({'message': 'Patient not found'}), 404

    pregnancy_history = PregnancyHistory(**data)
    pregnancy_history.patient = patient
    db.session.add(pregnancy_history)
    db.session.commit()

    return jsonify(
        {"message": f"Pregnancy History for patient id {patient.id} created successfully"}
    ), 201


# get a patient's pregnancy history
@api_bp.route('/patients/<int:patient_id>/pregnancy-history', methods=['GET'], strict_slashes=False)
@admin_or_provider_required
@jwt_required()
def get_pregnancy_history(patient_id):
    """Get a patient's pregnancy history."""

    patient = db.session.query(Patient).get(patient_id)
    if not patient:
        return jsonify({'message': 'Patient not found'}), 404

    pregnancy_history = db.session.query(PregnancyHistory).filter_by(patient_id=patient.id).first()
    if not pregnancy_history:
        return jsonify({'message': 'Pregnancy history not found'}), 404

    return jsonify(pregnancy_history.to_dict()), 200


# get a patient's pregnancy history (self)
@api_bp.route('/patients/me/pregnancy-history', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_pregnancy_history_self():
    """Get a patient's pregnancy history."""

    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"message": "Token is missing"}), 401
    if token.startswith("Bearer "):  # strip the bearer prefix
        token = token[7:]

    current_user_id = decode_token(encoded_token=token)["sub"]

    patient = db.session.query(Patient).get(current_user_id)
    if not patient:
        return jsonify({'message': 'Patient not found'}), 404

    pregnancy_history = db.session.query(PregnancyHistory).filter_by(patient_id=patient.id).first()
    if not pregnancy_history:
        return jsonify({'message': 'Pregnancy history not found'}), 404

    return jsonify(pregnancy_history.to_dict()), 200


# update a patient's pregnancy history
@api_bp.route('/patients/<int:patient_id>/pregnancy-history', methods=['PUT'])
@admin_or_provider_required
@jwt_required()
def update_pregnancy_history(patient_id):
    """Update a patient's pregnancy history."""

    schema = PregnancyHistorySchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"message": "Invalid input data", "errors": err.messages}), 400

    patient = db.session.query(Patient).get(patient_id)
    if not patient:
        return jsonify({'message': 'Patient not found'}), 404

    pregnancy_history = db.session.query(PregnancyHistory).filter_by(patient_id=patient.id).first()
    if not pregnancy_history:
        return jsonify({'message': 'Pregnancy history not found'}), 404

    pregnancy_history.update(data)
    db.session.commit()

    return jsonify(
        {"message": f"Pregnancy History for patient id {patient.id} updated successfully"}
    ), 200


# delete a patient's pregnancy history
@api_bp.route('/patients/<int:patient_id>/pregnancy-history', methods=['DELETE'])
@admin_or_provider_required
@jwt_required()
def delete_pregnancy_history(patient_id):
    """Delete a patient's pregnancy history."""

    patient = db.session.query(Patient).get(patient_id)
    if not patient:
        return jsonify({'message': 'Patient not found'}), 404

    pregnancy_history = db.session.query(PregnancyHistory).filter_by(patient_id=patient.id).first()
    if not pregnancy_history:
        return jsonify({'message': 'Pregnancy history not found'}), 404

    db.session.delete(pregnancy_history)
    db.session.commit()

    return jsonify(
        {"message": f"Pregnancy History for patient id {patient.id} deleted successfully"}
    ), 200
