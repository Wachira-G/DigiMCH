"""Module to define api appoitment endpoints"""

from datetime import datetime
from flask import jsonify, request
from app import db
from api.v1.views import api_bp
from api.v1.views.user import admin_required
from api.v1.views.patient import admin_or_provider_required, patient_required, token_required
from models.appointment import Appointment
from models.user import User
from models.patient import Patient

time = "%Y-%m-%dT%H:%M:%S"


@api_bp.route('/appointments', methods=['GET'], strict_slashes=False)
@token_required(User)
@admin_or_provider_required
def get_all_appointments(current_user):
    """Get all appointments"""
    appointments = db.session.query(Appointment).all()
    return jsonify([appointment.to_dict() for appointment in appointments]), 200

# create an appointment
@api_bp.route('/appointments', methods=['POST'], strict_slashes=False)
@token_required(User)
@admin_or_provider_required
def create_appointment(current_user):
    """Create an appointment"""
    data = request.get_json()
    data['user_id'] = current_user.id
    appointment = Appointment(**data)
    appointment.save()
    return jsonify(appointment.to_dict()), 201

# update an appointment (status, type, date)
@api_bp.route('/appointments/<int:appointment_id>', methods=['PUT'], strict_slashes=False)
@token_required(User)
@admin_or_provider_required
def update_appointment(current_user, appointment_id):
    """Update an appointment"""
    appointment = db.session.query(Appointment).get(appointment_id)
    if not appointment:
        return jsonify({'error': 'Appointment not found'}), 404
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Not a JSON'}), 400
    for key, value in data.items():
        if key in ["appointment_status", "appointment_type", "appointment_date"]:
            if key == "appointment_date":
                try:
                    setattr(appointment, key, datetime.strptime(value, time))
                except ValueError:
                    raise ValueError(f"Invalid date format. Should be {time}")
            else:
                setattr(appointment, key, value)
    db.session.commit()
    return jsonify(appointment.to_dict()), 200

# delete an appointment
@api_bp.route('/appointments/<int:appointment_id>', methods=['DELETE'], strict_slashes=False)
@token_required(User)
@admin_or_provider_required
def delete_appointment(current_user, appointment_id):
    """Delete an appointment"""
    appointment = db.session.query(Appointment).get(appointment_id)
    if not appointment:
        return jsonify({'error': 'Appointment not found'}), 404
    db.session.delete(appointment)
    db.session.commit()
    return jsonify({'message': 'Appointment deleted'}), 200

# get all appointments for a patient
@api_bp.route('/appointments/patient/<int:patient_id>', methods=['GET'], strict_slashes=False)
@token_required(User)
@admin_or_provider_required
def get_patient_appointments(current_user, patient_id):
    """Get all appointments for a patient"""
    appointments = db.session.query(Appointment).filter_by(patient_id=patient_id).all()
    return jsonify([appointment.to_dict() for appointment in appointments]), 200

# get all appointments for a patient (self)
@api_bp.route('/appointments/patient/me', methods=['GET'], strict_slashes=False)
@token_required(Patient)
@patient_required
def get_patient_self_appointments(current_user):
    """Get all appointments for a patient"""
    appointments = db.session.query(Appointment).filter_by(patient_id=current_user.id).all()
    return jsonify([appointment.to_dict() for appointment in appointments]), 200

# request for reschedule for an appointment by patient---TODO

# get all appointments for a user
@api_bp.route('/appointments/user/<int:user_id>', methods=['GET'], strict_slashes=False)
@token_required(User)
@admin_or_provider_required
def get_user_appointments(current_user, user_id):
    """Get all appointments for a user"""
    appointments = db.session.query(Appointment).filter_by(user_id=user_id).all()
    return jsonify([appointment.to_dict() for appointment in appointments]), 200

# get all appointments for a user (self)
@api_bp.route('/appointments/user/me', methods=['GET'], strict_slashes=False)
@token_required(User)
@admin_or_provider_required
def get_user_self_appointments(current_user):
    """Get all appointments for a user"""
    appointments = db.session.query(Appointment).filter_by(user_id=current_user.id).all()
    return jsonify([appointment.to_dict() for appointment in appointments]), 200
