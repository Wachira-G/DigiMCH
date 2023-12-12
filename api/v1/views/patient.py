"""Patient views."""


from flask import jsonify, request, abort
from flask_jwt_extended import jwt_required, decode_token
from functools import wraps
from app import db
from api.v1.views import api_bp
from models.patient import Patient
from models.person import Person
from models.role import Role
from models.user import User
from auth.validators import valid_date


admin_role = db.session.query(Role).filter_by(name="admin").first()
provider_role = db.session.query(Role).filter_by(name="provider").first()
patient_role = db.session.query(Role).filter_by(name="patient").first()


def role_required(*required_roles):
    """Decorator to check if a user has the required role(s)."""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
        # Get the auth token
            token = request.headers.get("Authorization")
            if not token:
                return jsonify({"message": "Token is missing"}), 401
            if token.startswith("Bearer "):  # strip the bearer prefix
                token = token[7:]

            current_user_id = decode_token(encoded_token=token)["sub"]

            # Get the current user
            if current_user_id is None:
                return (
                    jsonify(
                        {"message": "Authentication is required to access this resource"}
                    ),
                    401,
                )
            current_user = db.session.get(Person, current_user_id)
            if current_user is None:
                return (
                    jsonify(
                        {"message": "Authentication is required to access this resource"}
                    ),
                    401,
                )

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

            return f(*args, **kwargs)

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
@admin_or_provider_required
@jwt_required()
def get_patients():
    """Return all patients."""
    patients = db.session.query(Patient).all()
    return jsonify([patient.to_dict() for patient in patients]), 200


# endpoint to get a single patient by id
# requres admin or provider role
# or patient if logged in user is patient and id matches logged in user's id TODO
@api_bp.route("/patients/<string:patient_id>", methods=["GET"], strict_slashes=False)
@admin_or_provider_required
@jwt_required()
def get_patient(patient_id):
    """Return a single patient."""
    patient = db.session.query(Patient).get(patient_id)
    if not patient:
        abort(404)
    return jsonify(patient.to_dict()), 200


# endpoint to get a single patient by phone_no
# requres admin or provider role
# or patient if logged in user is patient and phone_no matches logged in user's phone_no
@api_bp.route("/patients/phone/<string:phone_no>", methods=["GET"], strict_slashes=False)
@api_bp.route("/patients/phone_no/<string:phone_no>", methods=["GET"], strict_slashes=False)
@admin_or_provider_required
@jwt_required()
def get_patient_by_phone_no(phone_no):
    """Return a single patient."""
    patient = db.session.query(Patient).filter_by(phone_no=phone_no).first()
    if not patient:
        abort(404)
    return jsonify(patient.to_dict()), 200


# get patient's info(self) for the currnet logged in patient
@api_bp.route("/patients/me", methods=["GET"], strict_slashes=False)
@patient_required
@jwt_required()
def get_patient_self():
    """Return a single patient."""
    token = request.headers.get("Authorization")
    patient = None
    if token:
        if token.startswith("Bearer "):
            token = token[7:]
        current_user_id = decode_token(encoded_token=token)["sub"]
        patient = db.session.query(Patient).filter_by(id=current_user_id).first()

    # patient = (
    #     db.session.query(Patient).filter_by(phone_no=current_user.phone_no).first()
    # )
    if not patient:
        abort(404)
    return jsonify(patient.to_dict()), 200


def get_role(name):
    """Return a role by name - helper function."""
    if name:
        name = name.lower()
    role = db.session.query(Role).filter_by(name=name).first()
    return role

# endpoint to create a patient
# requres admin or provider role
@api_bp.route("/patients", methods=["POST"], strict_slashes=False)
@admin_or_provider_required
@jwt_required()
def create_patient():
    """Create a patient."""
    data = request.get_json()
    if not data:
        abort(400, "Invalid data")

    for field in ["first_name", "surname", "phone_no", "sex", "birth_date", "password"]:
        if field not in data:
            abort(400, f"Missing required field: {field}")

    phone_no_exists = db.session.query(Person).filter_by(phone_no=data["phone_no"]).first()
    if phone_no_exists:
        abort(400, f"A user with Phone number already exists: {data['phone_no']}")

    roles = []
    if "role" in data:
        role = get_role(data["role"])
        if not role:
            abort(400, f'Invalid role: {data["role"]}')
        roles.append(role)
        del data["role"]

    if "roles" in data:
        for role_name in data["roles"]:
            role = get_role(role_name)
            if not role:
                abort(400, f"Invalid role: {role_name}")
            roles.append(role)
        del data["roles"]

    roles = list(set(roles))  # remove duplicates

    if "birth_date" in data:
        if valid_date(data["birth_date"]):
            pass
        else:
            abort(
                400,
                f"Invalid date: {data['birth_date']}, date format should be YYYY-MM-DDT00:00:00"
            )


    patient = Patient(**data)
    if not patient:
        abort(400, "Failed to create patient")

    patient.roles.extend(roles)
    db.session.add(patient)
    db.session.commit()
    return jsonify(patient.to_dict()), 201


# endpoint to update a patient
# requres admin or provider role
@api_bp.route("/patients/<string:patient_id>", methods=["PUT"], strict_slashes=False)
@admin_or_provider_required
@jwt_required()
def update_patient(patient_id):
    """Update a patient."""
    patient = db.session.query(Patient).get(patient_id)
    if not patient:
        abort(404)
    data = request.get_json()
    if not data:
        abort(400)
    for key, value in data.items():
        if key in ["first_name", "surname", "middle_name", "phone_no"]: # TODO add more fields
            setattr(patient, key, value)
    db.session.commit()
    return jsonify(patient.to_dict()), 200


# endpoint to update a patient's limited details
# requires that user has patient role and phone_no matches logged in user's phone_no


# endpoint to delete a patient
# requres admin or provider role
@api_bp.route("/patients/<string:patient_id>", methods=["DELETE"], strict_slashes=False)
@admin_or_provider_required
@jwt_required()
def delete_patient(patient_id):
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
