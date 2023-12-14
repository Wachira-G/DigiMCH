"""Antenatal profile endpoints."""

from flask import request, jsonify
from flask_jwt_extended import jwt_required, decode_token
from marshmallow import ValidationError, schema, fields

from app import db
from api.v1.views import api_bp
from api.v1.views.patient import admin_or_provider_required
from models.antenatal_profile import AntenatalProfile
from models.patient import Patient


class AntenatalProfileSchema(schema.Schema):
    """Antenatal profile schema."""

    id = fields.Integer()
    patient_id = fields.Integer()
    hemoglobin = fields.Float()
    blood_group = fields.String()
    rhesus = fields.String()
    urinalysis = fields.String()
    blood_rbs = fields.Float()
    tb_screening_tool = fields.Boolean()
    tb_screening_outcome = fields.String()
    isoniazid_preventive_therapy = fields.Boolean()
    ipt_given_date = fields.Date()
    next_visit_date = fields.Date()
    obstetric_ultrasound_first_done = fields.Boolean()
    first_ultrasound_gestation = fields.Integer()
    first_ultrasound_date = fields.Date()
    obstetric_ultrasound_second_done = fields.Boolean()
    second_ultrasound_gestation = fields.Integer()
    second_ultrasound_date = fields.Date()
    triple_testing_date = fields.Date()
    hiv_test_result = fields.String()
    syphilis_test_result = fields.String()
    hepatitis_b_test_result = fields.String()
    hiv_non_reactive_retesting_date = fields.Date()
    couple_hiv_counseling_done = fields.Boolean()
    partner_hiv_status = fields.String()


# create a patient's antenatal profile
@api_bp.route("/patients/<int:patient_id>/antenatal_profile", methods=["POST"], strict_slashes=False)
@admin_or_provider_required
@jwt_required()
def create_antenatal_profile(patient_id):
    """Create a patient's antenatal profile."""
    schema = AntenatalProfileSchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    patient = db.session.query(Patient).get(patient_id)
    if not patient:
        return jsonify({"message": "Patient not found."}), 404
    
    try:
        antenatal_profile = AntenatalProfile(**data)
    except Exception as err:
        return jsonify({"message": f"Failed to create antenatal profile: {err}."}), 400
    
    antenatal_profile.patient = patient
    db.session.add(antenatal_profile)
    db.session.commit()

    return jsonify({"message": "Antenatal profile created successfully."}), 201



# get a patient's antenatal profile
@api_bp.route("/patients/<int:patient_id>/antenatal_profile", methods=["GET"], strict_slashes=False)
@admin_or_provider_required
@jwt_required()
def get_antenatal_profile(patient_id):
    """Get a patient's antenatal profile."""
    antenatal_profile = db.session.query(AntenatalProfile).filter_by(patient_id=patient_id).first()
    if not antenatal_profile:
        return jsonify({"message": "Antenatal profile not found."}), 404
    
    schema = AntenatalProfileSchema()
    return jsonify(schema.dump(antenatal_profile)), 200


# get a patient's antenatal profile (self)
@api_bp.route("/patients/me/antenatal_profile", methods=["GET"], strict_slashes=False)
@jwt_required()
def get_antenatal_profile_self():
    """Get a patient's antenatal profile."""
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

    antenatal_profile = db.session.query(AntenatalProfile).filter_by(patient_id=patient_id).first()
    if not antenatal_profile:
        return jsonify({"message": "Antenatal profile not found."}), 404
    
    schema = AntenatalProfileSchema()
    return jsonify(schema.dump(antenatal_profile)), 200

# update a patient's antenatal profile
@api_bp.route("/patients/<int:patient_id>/antenatal_profile", methods=["PUT"], strict_slashes=False)
@admin_or_provider_required
@jwt_required()
def update_antenatal_profile(patient_id):
    """Update a patient's antenatal profile."""
    schema = AntenatalProfileSchema()
    try:
        data = schema.load(request.get_json(), partial=True)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    antenatal_profile = db.session.query(AntenatalProfile).filter_by(patient_id=patient_id).first()
    if not antenatal_profile:
        return jsonify({"message": "Antenatal profile not found."}), 404
    
    try:
        for key, value in data.items():
            setattr(antenatal_profile, key, value)
    except Exception as err:
        return jsonify({"message": f"Failed to update antenatal profile: {err}."}), 400
    
    db.session.commit()

    return jsonify({"message": "Antenatal profile updated successfully."}), 200


# delete a patient's antenatal profile
@api_bp.route("/patients/<int:patient_id>/antenatal_profile", methods=["DELETE"], strict_slashes=False)
@admin_or_provider_required
@jwt_required()
def delete_antenatal_profile(patient_id):
    """Delete a patient's antenatal profile."""
    antenatal_profile = db.session.query(AntenatalProfile).filter_by(patient_id=patient_id).first()
    if not antenatal_profile:
        return jsonify({"message": "Antenatal profile not found."}), 404
    
    db.session.delete(antenatal_profile)
    db.session.commit()

    return jsonify({"message": "Antenatal profile deleted successfully."}), 200
