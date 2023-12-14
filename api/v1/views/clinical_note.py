"""Clinical Note Endpoints."""

from flask import jsonify, request
from flask_jwt_extended import jwt_required, decode_token
from marshmallow import ValidationError, schema, fields

from app import db
from api.v1.views import api_bp
from api.v1.views.patient import admin_or_provider_required
from models.clinical_note import ClinicalNote
from models.patient import Patient


class ClinicalNoteSchema(schema.Schema):
    """Clinical note schema."""

    id = fields.Integer(dump_only=True)
    patient_id = fields.Integer()
    notes = fields.String()
    date = fields.Date()
    next_visit_date = fields.Date()

    # created_by = fields.String()


# create a patient's clinical note
@api_bp.route("/patients/<int:patient_id>/clinical_notes", methods=["POST"], strict_slashes=False)
@admin_or_provider_required
@jwt_required()
def create_clinical_note(patient_id):
    """Create a patient's clinical note."""
    schema = ClinicalNoteSchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify(err.messages), 400

    patient = db.session.query(Patient).get(patient_id)
    if not patient:
        return jsonify({"message": "Patient not found."}), 404

    try:
        clinical_note = ClinicalNote(**data)

    except Exception as err:
        return jsonify({"message": f"Failed to create clinical note: {err}."}), 400

    clinical_note.patient = patient

    db.session.add(clinical_note)
    db.session.commit()

    return jsonify({"message": "Clinical note created successfully."}), 201


# get a patient's clinical notes
@api_bp.route("/patients/<int:patient_id>/clinical_notes", methods=["GET"], strict_slashes=False)
@admin_or_provider_required
@jwt_required()
def get_clinical_note(patient_id):
    """Get a patient's clinical note."""
    patient = db.session.query(Patient).get(patient_id)
    if not patient:
        return jsonify({"message": "Patient not found."}), 404

    clinical_notes = patient.clinical_notes
    if not clinical_notes:
        return jsonify({"message": "Clinical notes not found."}), 404

    schema = ClinicalNoteSchema(many=True)
    return jsonify(schema.dump(clinical_notes)), 200


# get a patient's clinical notes  (self)
@api_bp.route("/patients/me/clinical_notes", methods=["GET"], strict_slashes=False)
@jwt_required()
def get_clinical_note_self():
    """Get a patient's clinical note."""
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

    clinical_notes = patient.clinical_notes
    if not clinical_notes:
        return jsonify({"message": "Clinical notes not found."}), 404

    schema = ClinicalNoteSchema(many=True)
    return jsonify(schema.dump(clinical_notes)), 200


# update a patient's clinical note
@api_bp.route("/patients/<int:patient_id>/clinical_notes/<int:clinical_note_id>", methods=["PUT"], strict_slashes=False)
@admin_or_provider_required
@jwt_required()
def update_clinical_note(patient_id, clinical_note_id):
    """Update a patient's clinical note."""
    schema = ClinicalNoteSchema()
    try:
        data = schema.load(request.get_json(), partial=True)
    except ValidationError as err:
        return jsonify(err.messages), 400

    patient = db.session.query(Patient).get(patient_id)
    if not patient:
        return jsonify({"message": "Patient not found."}), 404

    clinical_note = db.session.query(ClinicalNote).get(clinical_note_id)
    if not clinical_note:
        return jsonify({"message": "Clinical note not found."}), 404

    for key, value in data.items():
        setattr(clinical_note, key, value)

    db.session.commit()

    return jsonify({"message": "Clinical note updated successfully."}), 200


# delete a patient's clinical note
@api_bp.route("/patients/<int:patient_id>/clinical_notes/<int:clinical_note_id>", methods=["DELETE"], strict_slashes=False)
@admin_or_provider_required
@jwt_required()
def delete_clinical_note(patient_id, clinical_note_id):
    """Delete a patient's clinical note."""
    patient = db.session.query(Patient).get(patient_id)
    if not patient:
        return jsonify({"message": "Patient not found."}), 404

    clinical_note = db.session.query(ClinicalNote).get(clinical_note_id)
    if not clinical_note:
        return jsonify({"message": "Clinical note not found."}), 404

    db.session.delete(clinical_note)
    db.session.commit()

    return jsonify({"message": "Clinical note deleted successfully."}), 200
