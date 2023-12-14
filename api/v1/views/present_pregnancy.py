from flask import request, jsonify
from flask_jwt_extended import jwt_required, decode_token
from marshmallow import ValidationError, schema, fields
from sqlalchemy.exc import NoResultFound

from app import db
from api.v1.views import api_bp
from api.v1.views.patient import admin_or_provider_required
from models.present_pregnancy import PresentPregnancy
from models.patient import Patient


class PresentPregnancySchema(schema.Schema):
    """Present pregnancy schema."""

    id = fields.Int(dump_only=True)
    patient_id = fields.Int(required=False)
    number_of_contacts = fields.Int(required=False)
    date = fields.Date(required=True)
    urine = fields.Str()
    muac = fields.Float()
    blood_pressure_systolic = fields.Int()
    blood_pressure_diastolic = fields.Int()
    hemoglobin = fields.Float()
    pallor = fields.Bool()
    gestation_in_weeks = fields.Int()
    fundal_height = fields.Float()
    presentation = fields.Str()
    lie = fields.Str()
    fetal_heart_rate = fields.Int()
    fetal_movement = fields.Str()
    next_visit_date = fields.Date()


    class Meta:
        ordered = True


# GET /patients/{patient_id}/present_pregnancy:
# This endpoint would return the present pregnancy instances for a specific patient.
@api_bp.route('/patients/<int:patient_id>/present_pregnancy', methods=['GET'], strict_slashes=False)
@admin_or_provider_required
@jwt_required()
def get_present_pregnancies(patient_id):
    """Get present pregnancies for a specific patient."""
    try:
        patient = db.session.query(Patient).get(patient_id)
    except NoResultFound:
        return jsonify({'message': 'Patient not found'}), 404

    present_pregnancies = patient.present_pregnancy
    schema = PresentPregnancySchema(many=True)
    return jsonify(schema.dump(present_pregnancies))


# GET /patients/{patient_id}/present_pregnancy/<int:id>:
# This endpoint would return the a present pregnancy instance for a specific patient.
@api_bp.route('/patients/<int:patient_id>/present_pregnancy/<int:id>', methods=["GET"], strict_slashes=False)
@admin_or_provider_required
@jwt_required()
def get_present_pregnancy_by_id(patient_id, id):
    """Get a present pregnancy instance for a specific patient."""
    try:
        patient = db.session.query(Patient).get(patient_id)
    except NoResultFound:
        return jsonify({"message": "Patient not found"}), 404

    present_pregnancy = next((pp for pp in patient.present_pregnancy if pp.id == id), None)
    if present_pregnancy:
        schema = PresentPregnancySchema()
        return jsonify(schema.dump(present_pregnancy)), 200
    else:
        return jsonify({"message": "Present pregnancy instance not found."}), 404


# POST /patients/{patient_id}/present_pregnancy
@api_bp.route(
    "/patients/<int:patient_id>/present_pregnancy", methods=["POST"], strict_slashes=False 
)
@admin_or_provider_required
@jwt_required()
def create_present_pregnacy(patient_id):
    """Create a present pregnacny anc visit record for a patient."""
    schema = PresentPregnancySchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify(err.messages), 422

    patient = db.session.query(Patient).get(patient_id)
    if not patient:
        return jsonify({"message": "Patient not found"}), 404

    try:
        present_pregnancy_instance = PresentPregnancy(**data)

    except Exception as e:
        return jsonify({'message': f"Failed creating the present pregnancy instance {e}."}), 500
    
    present_pregnancy_instance.patient = patient

    db.session.add(present_pregnancy_instance)
    db.session.commit()

    return jsonify({
        "message": "Present pregnancy instance created"
    }), 201

# PUT /patients/{patient_id}/present_pregnancy/<int:id>
@api_bp.route(
    "/patients/<int:patient_id>/present_pregnancy/<int:id>", methods=["PUT"], strict_slashes=False
)
@admin_or_provider_required
@jwt_required()
def update_present_pregnancy(patient_id, id):
    """Update a present pregnancy instance for a patient."""
    schema = PresentPregnancySchema(partial=True)
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify(err.messages), 422

    patient = db.session.query(Patient).get(patient_id)
    if not patient:
        return jsonify({"message": "Patient not found"}), 404

    present_pregnancy = next((pp for pp in patient.present_pregnancy if pp.id == id), None)
    if not present_pregnancy:
        return jsonify({"message": "Present pregnancy instance not found."}), 404

    try:
        for key, value in data.items():
            setattr(present_pregnancy, key, value)
    except Exception as e:
        return jsonify({'message': f"Failed updating the present pregnancy instance {e}."}), 500

    db.session.add(present_pregnancy)
    db.session.commit()

    return jsonify({
        "message": "Present pregnancy instance updated"
    }), 200


# DELETE /patients/{patient_id}/present_pregnancy/<int:id>
@api_bp.route(
    "/patients/<int:patient_id>/present_pregnancy/<int:id>", methods=["DELETE"], strict_slashes=False
)
@admin_or_provider_required
@jwt_required()
def delete_present_pregnancy(patient_id, id):
    """Delete a present pregnancy instance for a patient."""
    patient = db.session.query(Patient).get(patient_id)
    if not patient:
        return jsonify({"message": "Patient not found"}), 404

    present_pregnancy = next((pp for pp in patient.present_pregnancy if pp.id == id), None)
    if not present_pregnancy:
        return jsonify({"message": "Present pregnancy instance not found."}), 404

    try:
        db.session.delete(present_pregnancy)
        db.session.commit()
    except Exception as e:
        return jsonify({'message': f"Failed deleting the present pregnancy instance {e}."}), 500

    return jsonify({
        "message": "Present pregnancy instance deleted"
    }), 200


# GET /patients/me/present_pregnancy:
# This endpoint would return the present pregnancy instances for the current logged in patient.
@api_bp.route('/patients/me/present_pregnancy', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_present_pregnancies_for_current_patient():
    """Get present pregnancies for the current logged in patient."""
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
    present_pregnancies = patient.present_pregnancy
    schema = PresentPregnancySchema(many=True)
    return jsonify(schema.dump(present_pregnancies))


# GET /patients/me/present_pregnancy/<int:id>:
# This endpoint would return the a present pregnancy instance for the current logged in patient.
@api_bp.route('/patients/me/present_pregnancy/<int:id>', methods=["GET"], strict_slashes=False)
@jwt_required()
def get_present_pregnancy_by_id_for_current_patient(id):
    """Get a present pregnancy instance for the current logged in patient."""
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

    present_pregnancy = next((pp for pp in patient.present_pregnancy if pp.id == id), None)
    if present_pregnancy:
        schema = PresentPregnancySchema()
        return jsonify(schema.dump(present_pregnancy)), 200
    else:
        return jsonify({"message": "Present pregnancy instance not found."}), 404
