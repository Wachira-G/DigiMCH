from flask import jsonify, request, abort
from functools import wraps
from app import db
from api.v1.views import api_bp
from models.patient import Patient
from models.person import Person
from models.role import Role
from models.user import User

admin_role = Role.query.filter_by(name="admin").first()
provider_role = Role.query.filter_by(name="provider").first()
patient_role = Role.query.filter_by(name="patient").first()


def token_required(model):
    """Decorator to check if a user is logged in."""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get the auth token
            token = request.headers.get("Authorization")
            if not token:
                return jsonify({"message": "Token is missing"}), 401

            # Get the current user
            current_user = Person.verify_auth_token(token, model)
            if current_user is None:
                return (
                    jsonify(
                        {
                            "message": "Authentication is required to access this resource"
                        }
                    ),
                    401,
                )

            return f(current_user, *args, **kwargs)

        return decorated_function

    return decorator


def role_required(*required_roles):
    """Decorator to check if a user has the required role(s)."""

    def decorator(f):
        @wraps(f)
        def decorated_function(current_user, *args, **kwargs):
            # Check if the current user has any of the required roles
            if not any(
                role in (role.name for role in current_user.roles)
                for role in required_roles
            ):
                return (
                    jsonify(
                        {
                            "message": f'{"/".join(required_roles).capitalize()} privileges are required to access this resource'
                        }
                    ),
                    403,
                )

            return f(current_user, *args, **kwargs)

        return decorated_function

    return decorator


# decorator to check if user is admin
admin_required = role_required("admin")

# decorator to check if user is provider
provider_required = role_required("provider")

# decorator to check if user is patient and user.id matches patient.id
#  or user.phone_no matches patient.phone_no ---> TODO
patient_required = role_required("patient")

# decorator to check if user is admin or provider
admin_or_provider_required = role_required("admin", "provider")

# --------------------ENDPOINTS ---------------------------

# endpoint to get all patients
# requres admin or provider role
@api_bp.route("/patients", methods=["GET"], strict_slashes=False)
@token_required(User)
@admin_or_provider_required
def get_patients(current_user):
    """Return all patients."""
    patients = db.session.query(Patient).all()
    return jsonify([patient.to_dict() for patient in patients]), 200


# endpoint to get a single patient by id
# requres admin or provider role
# or patient if logged in user is patient and id matches logged in user's id TODO
@api_bp.route("/patients/<string:patient_id>", methods=["GET"], strict_slashes=False)
@token_required(User)
@admin_or_provider_required
def get_patient(current_user, patient_id):
    """Return a single patient."""
    patient = db.session.query(Patient).get(patient_id)
    if not patient:
        abort(404)
    return jsonify(patient.to_dict()), 200


# endpoint to get a single patient by phone_no
# requres admin or provider role
# or patient if logged in user is patient and phone_no matches logged in user's phone_no
@api_bp.route("/patients/<string:phone_no>", methods=["GET"], strict_slashes=False)
@token_required(User)
@admin_or_provider_required
def get_patient_by_phone_no(current_user, phone_no):
    """Return a single patient."""
    patient = db.session.query(Patient).filter_by(phone_no=phone_no).first()
    if not patient:
        abort(404)
    return jsonify(patient.to_dict()), 200


# THIS ENDPOINT DOES NOT MAKE SENSE
# endpoint to get a single patient by phone_no by patient if logged in user is patient and phone_no matches logged in user's phone_no
@api_bp.route("/patients/me", methods=["GET"], strict_slashes=False)
@token_required(Patient)
@patient_required
def get_patient_self(current_user):
    """Return a single patient."""
    patient = (
        db.session.query(Patient).filter_by(phone_no=current_user.phone_no).first()
    )
    if not patient:
        abort(404)
    return jsonify(patient.to_dict()), 200


# endpoint to create a patient
# requres admin or provider role
@api_bp.route("/patients", methods=["POST"], strict_slashes=False)
@token_required(User)
@admin_or_provider_required
def create_patient(current_user):
    """Create a patient."""
    data = request.get_json()
    patient = Patient(**data)
    db.session.add(patient)
    db.session.commit()
    return jsonify(patient.to_dict()), 201


# endpoint to update a patient
# requres admin or provider role
@api_bp.route("/patients/<string:patient_id>", methods=["PUT"], strict_slashes=False)
@token_required(User)
@admin_or_provider_required
def update_patient(current_user, patient_id):
    """Update a patient."""
    patient = db.session.query(Patient).get(patient_id)
    if not patient:
        abort(404)
    data = request.get_json()
    if not data:
        abort(400)
    for key, value in data.items():
        if key in ["first_name", "surname", "middle_name", "phone_no", "email"]:
            setattr(patient, key, value)
    db.session.commit()
    return jsonify(patient.to_dict()), 200


# endpoint to update a patient's limited details
# requires that user has patient role and phone_no matches logged in user's phone_no


# endpoint to delete a patient
# requres admin or provider role
@api_bp.route("/patients/<string:patient_id>", methods=["DELETE"], strict_slashes=False)
@token_required(User)
@admin_or_provider_required
def delete_patient(current_user, patient_id):
    """Delete a patient."""
    patient = db.session.query(Patient).get(patient_id)
    if not patient:
        abort(404)
    db.session.delete(patient)
    db.session.commit()
    return jsonify({"message": "Patient deleted"}), 200


# endpoint for a patient profile admin or provider role (full details,
#  visits(with encounters), appointments, [add more])

# endpoint for a patient profile self
