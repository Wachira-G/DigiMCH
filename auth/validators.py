"""Validation helpers for auth app."""

# data validation  for all inputs- password, email, phone number, etc

from flask import jsonify
import re
from models.person import Person
from models.user import User
from models.patient import Patient


def is_valid_kenyan_phone(phone_no):
    """Check if a phone number is valid.
    Phone number must be in the format +2547XXXXXXXX or +25410XXXXXXXX or +25411XXXXXXXX.
    """
    pattern = r"^\+254(7|10|11)[0-9]{8}$"
    return bool(re.match(pattern, phone_no))


def is_valid_password(password):
    """Check if a password is valid.
    Password must be at least 8 characters long and contain at least one letter and one number.
    """
    pattern = r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$"
    return bool(re.match(pattern, password))


def get_user_or_patient(phone_no):
    person = Person.query.filter_by(phone_no=phone_no).first()
    if not person:
        return None

    if person.type == "user":
        return User.query.filter_by(phone_no=phone_no).first()
    elif person.type == "patient":
        return Patient.query.filter_by(phone_no=phone_no).first()


def error_response(message, status_code):
    return jsonify({"message": message}), status_code


def validate_phone_no(phone_no):
    if not phone_no or not is_valid_kenyan_phone(phone_no):
        return False, error_response("Please provide a valid Kenyan phone number", 400)
    return True, None


def validate_password(password):
    if not password or not is_valid_password(password):
        return False, error_response("Please provide valid password", 400)
    return True, None

def valid_date(date):
    """Check if a date is valid.
    Date must be in the format '%Y-%m-%dT%H:%M:%S'.
    """
    pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$"
    return bool(re.match(pattern, date))