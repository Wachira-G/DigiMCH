"""First visit examination endpoints."""

from flask import request, jsonify
from flask_jwt_extended import jwt_required, decode_token
from marshmallow import ValidationError, schema, fields

from app import db
from api.v1.views import api_bp
from api.v1.views.patient import admin_or_provider_required
from models.first_visit_examination import PhysicalExaminationFirstVisit
from models.patient import Patient


class PhysicalExaminationFirstVisitSchema(schema.Schema):
    """Physical examination first visit schema."""

    id = fields.Int(dump_only=True)
    patient_id = fields.Int(required=False)
    general_examination = fields.Str(required=True)
    blood_pressure_systolic = fields.Int(required=True)
    blood_pressure_diastolic = fields.Int(required=True)
    pulse_rate = fields.Int(required=True)
    cardiovascular_system = fields.Str(required=True)
    respiratory_system = fields.Str(required=True)
    abdomen = fields.Str(required=True)
    breasts = fields.Str()
    external_genitalia_examination = fields.Str(required=True)
    discharge_present = fields.Bool(required=True)
    discharge_characteristics = fields.Str(required=False, allow_none=True)
    genital_ulcer_present = fields.Bool(required=True)
    genital_ulcer_characteristics = fields.Str(required=False, allow_none=True)


   
# GET /patients/{patient_id}/first_visit_examination:
# This endpoint would return the first visit examinations data for a specific patient.
@api_bp.route(
    '/patients/<int:patient_id>/first_visit_examination', methods=['GET'], strict_slashes=False
)
@admin_or_provider_required
@jwt_required()
def get_first_visit_examination(patient_id):
    """Get first visit examination for a specific patient."""
    first_visit_examination = db.session.query(PhysicalExaminationFirstVisit).filter_by(patient_id=patient_id).first()
    if not first_visit_examination:
        return jsonify({'message': 'First visit examination not found'}), 404

    schema = PhysicalExaminationFirstVisitSchema()
    return jsonify(schema.dump(first_visit_examination)), 200

# GET /patients/me/first_visit_examination
# This endpoint would return the first visit examination data for the logged in patient
@api_bp.route(
    '/patients/me/first_visit_examination', methods=['GET'], strict_slashes=False
)
@jwt_required()
def get_first_visit_examination_for_logged_in_patient():
    """Get first visit examination for logged in patient."""
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"message": "Missing authorization header"}), 401

    token = token.split(" ")[1]
    patient_id = decode_token(token)["sub"]
    patient = db.session.query(Patient).get(patient_id)
    if not patient:
        return jsonify({"message": "User not found"}), 404
    
    first_visit_examination = db.session.query(PhysicalExaminationFirstVisit).filter_by(patient_id=patient_id).first()
    if not first_visit_examination:
        return jsonify({'message': 'First visit examination not found'}), 404
    
    schema = PhysicalExaminationFirstVisitSchema()
    return jsonify(schema.dump(first_visit_examination)), 200



# POST /patients/{patient_id}/first_visit_examination: 
# This endpoint would create a first visit examination for a specific patient if it doesn't exist.
# Return error if it exists and communicate so.
@api_bp.route(
    '/patients/<int:patient_id>/first_visit_examination', methods=['POST'], strict_slashes=False
)
@admin_or_provider_required
@jwt_required()
def create_first_visit_examination(patient_id):
    """Create a first visit examination for a specific patient."""
    schema = PhysicalExaminationFirstVisitSchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify(err.messages), 422

    patient = db.session.query(Patient).get(patient_id)
    if not patient:
        return jsonify({"message": "Patient not found"}), 404

    first_visit_examination = patient.physical_examinations_first_visit
    if first_visit_examination:
        return jsonify({'message': 'First visit examination already exists'}), 409

    try:
        first_visit_examination = PhysicalExaminationFirstVisit(**data)

    except Exception as e:
        return jsonify({'message': f"Failed creating the first visit: {e}."}), 500
    
    first_visit_examination.patient = patient

    db.session.add(first_visit_examination)
    db.session.commit()
    return jsonify({'message': 'First visit examination created successfully'}), 201


# PUT /patients/{patient_id}/first_visit_examination: 
# This endpoint would update an existing first visit examination for a specific patient.
@api_bp.route(
    '/patients/<int:patient_id>/first_visit_examination', methods=['PUT'], strict_slashes=False
)
@admin_or_provider_required
@jwt_required()
def update_first_visit_examination(patient_id):
    """Update a first visit examination for a specific patient."""
    schema = PhysicalExaminationFirstVisitSchema()
    try:
        data = schema.load(request.get_json(), partial=True)
    except ValidationError as err:
        return jsonify(err.messages), 422

    patient = db.session.query(Patient).get(patient_id)
    if not patient:
        return jsonify({"message": "Patient not found"}), 404

    first_visit_examination = patient.physical_examinations_first_visit
    if not first_visit_examination:
        return jsonify({'message': 'First visit examination not found'}), 404

    try:
        first_visit_examination.update(data)

    except Exception as e:
        return jsonify({'message': f"Failed updating the first visit examination: {e}."}), 500

    return jsonify({'message': 'First visit examination updated successfully'}), 200

# DELETE /patients/{patient_id}/first_visit_examination: 
# This endpoint would delete a specific first visit examination for a specific patient.
@api_bp.route(
    '/patients/<int:patient_id>/first_visit_examination', methods=['DELETE'], strict_slashes=False
)
@admin_or_provider_required
@jwt_required()
def delete_first_visit_examination(patient_id):
    """Delete a first visit examination for a specific patient."""
    patient = db.session.query(Patient).get(patient_id)
    if not patient:
        return jsonify({"message": "Patient not found"}), 404

    first_visit_examination = patient.physical_examinations_first_visit
    if not first_visit_examination:
        return jsonify({'message': 'First visit examination not found'}), 404

    db.session.delete(first_visit_examination)
    db.session.commit()

    return jsonify({'message': 'First visit examination deleted successfully'}), 200
