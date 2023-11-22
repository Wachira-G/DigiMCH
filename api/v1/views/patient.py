
from api.v1.views import api_bp
from models.patient import Patient
from storage.db_storage import DbStorage
from flask import jsonify, request, abort, current_app
from sqlalchemy.orm import Session, sessionmaker, scoped_session

storage = current_app.config['storage']

@api_bp.route('/patients', methods=['GET'], strict_slashes=False)
def get_patients():
    """ Get all patients """
    patients = storage.all(Patient)
    return jsonify([patient.to_dict() for patient in patients])

@api_bp.route('/patients', methods=['POST'], strict_slashes=False)
def create_patient():
    """ Create a patient """
    patient = request.get_json()
    if 'first_name' not in patient:
        abort(400, 'Missing first_name')
    if 'surname' not in patient:
        abort(400, 'Missing surname')
    if 'middle_name' not in patient:
        abort(400, 'Missing middle_name')
    if 'phone_no' not in patient:
        abort(400, 'Missing phone_no')
    # if 'location_id' not in patient:

    patient_obj = Patient(**patient)
    print(patient_obj)
    storage.new(patient_obj)
    storage.save()
    return jsonify(patient_obj.to_dict()), 201


@api_bp.route('/patients/<id>', methods=['GET'], strict_slashes=False)
def get_patient(id):
    """ Get a patient """
    patient = storage.get(Patient, id)
    if not patient:
        abort(404)
    return jsonify(patient.to_dict()), 200


@api_bp.route('/patients/<id>', methods=['PUT'], strict_slashes=False)
def update_patient(id):
    """ Update a patient """
    patient = storage.get(Patient, id)
    if not patient:
        abort(404)
    patient_data = request.get_json()
    for key, value in patient_data.items():
        if key not in ['id', 'created_at', 'updated_at']:
            setattr(patient, key, value)
    storage.save()
    return jsonify(patient.to_dict()), 200


@api_bp.route('/patients/<id>', methods=['DELETE'], strict_slashes=False)
def delete_patient(id):
    """ Delete a patient """
    patient = storage.get(Patient, id)
    if not patient:
        abort(404)
    storage.delete(patient)
    storage.save()
    return jsonify({}), 200
