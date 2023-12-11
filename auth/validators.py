"""Validation helpers for auth app."""

# data validation  for all inputs- password, email, phone number, etc

from flask import jsonify
import re
from app import db
from models.location import Location, Tag
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


# -------------- Location related validators -----------------
def valid_location(data):
    """Check if a location is valid.
    Location must have a name and a tag.
    """
    if not data.get("name") or not data.get("tag"):
        return False
    return True


TAGS_HIERARCHY = [
    "country",
    "region",
    "county",
    "subcounty",
    "ward",
    "location",
    "sublocation",
    "neighbourhood",
    "village",
    "estate",
    "street",
    "building",
    "room",
]

# NOTE have to create all the tags first before the location


def valid_tag(tag):
    """Check if a tag is valid."""
    return bool(db.session.query(Tag).filter_by(name=tag).first())


def valid_tag_hierarchy(parent_tag, current_tag):
    try:
        parent_index = TAGS_HIERARCHY.index(parent_tag)
        current_index = TAGS_HIERARCHY.index(current_tag)
    except ValueError:
        return False  # One of the tags is not in the hierarchy

    return (
        current_index > parent_index
    )  # The current tag should be lower in the hierarchy


def location_exists(name, parent=None):
    """Check if a location exists."""
    locations = db.session.query(Location).filter_by(name=name).all()
    if not locations:
        return False

    if locations and parent:
        for location in locations:
            if location.parent_id == parent.id:
                return True
        return False
    # should i return true here (scenario?)


# -------------- End Location related validators -----------------
