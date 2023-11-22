
from api.v1.views import api_bp
from models.patient import Patient
from storage.db_storage import DbStorage
from flask import jsonify, request, abort, current_app
from sqlalchemy.orm import Session, sessionmaker, scoped_session


@api_bp.route('/patients', methods=['GET'], strict_slashes=False)
def get_patients():
    """ Get all patients """
    storage = current_app.config['storage']
    patients = storage.all(Patient)
    return jsonify([patient.to_dict() for patient in patients])

@api_bp.route('/patients', methods=['POST'], strict_slashes=False)
def create_patient():
    """ Create a patient """
    storage = current_app.config['storage']
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
