"""Authentication blueprint."""

from flask import abort, jsonify, request
from flask_jwt_extended import decode_token, get_jwt, get_jwt_identity, jwt_required
from api.v1.views.index import status

from auth import auth_bp
from auth.blocklist import TokenBlockList
from auth.validators import is_valid_kenyan_phone, is_valid_password

from app import db
from models.patient import Patient
from models.person import Person
from models.user import User


# api refresh token
@auth_bp.route("/api/v1/refresh", methods=["GET", "POST"], strict_slashes=False)
@jwt_required(refresh=True)
def refresh():
    """Refresh token."""
    current_user_id = get_jwt_identity()
    new_token = None
    if current_user_id:
        new_token = db.session.get(User, current_user_id).generate_access_token()
    return jsonify(access_token=new_token), 200


# api login
@auth_bp.route("/api/v1/login", methods=["GET"], strict_slashes=False)
def login():
    # if logged in
    # return jsonify({'message': 'Already logged in'})
    # else
    # show parameters to help user login
    token = request.headers.get("Authorization")
    person = Person.verify_auth_token(token, Person)
    if person:
        return jsonify({"message": "Already logged in"}), 200
    else:
        return (
            jsonify(
                {
                    "message": "Please login",
                    "parameters": {"phone_no": "phone number", "password": "password"},
                }
            ),
            401,
        )


# post login
@auth_bp.route("/api/v1/login", methods=["POST"], strict_slashes=False)
def login_post():
    data = request.get_json()

    valid, phone_no, password = validate_phone_passwd(data)
    if not valid:
        error_response = phone_no
        status_code = password
        return (
            error_response,
            status_code
        )

    success, user_or_patient_instance = get_user_or_patient(phone_no)
    if not success:
        return (
            user_or_patient_instance # is actually the error response
        ), 404

    authenticated, response = authenticate_user(user_or_patient_instance, password)
    if not authenticated:
        return response  # response is actually the error response

    return response


def validate_phone_passwd(data) -> tuple:
    """Validate phone number and password."""
    phone_no = data.get("phone_no")
    password = data.get("password")

    if not phone_no or not is_valid_kenyan_phone(phone_no):
        return (
            False,
            jsonify({"message": "Please provide a valid Kenyan phone number"}),
            400,
        )

    if not password or not is_valid_password(password):
        return False, jsonify({"message": "Please provide valid password"}), 400

    return True, phone_no, password


def get_user_or_patient(phone_no) -> tuple:
    """Get user or patient instance."""
    person = Person.query.filter_by(phone_no=phone_no).first()

    if not person:
        return False, jsonify({"message": "User not found"})

    user_or_patient_instance = None

    if person.type == "user":
        user_or_patient_instance = User.query.filter_by(phone_no=phone_no).first()
    elif person.type == "patient":
        user_or_patient_instance = Patient.query.filter_by(phone_no=phone_no).first()

    return True, user_or_patient_instance


def authenticate_user(user_or_patient_instance, password) -> tuple:
    """User authentication helper function."""
    if user_or_patient_instance and user_or_patient_instance.check_password(password):
        access_token = user_or_patient_instance.generate_access_token()
        refresh_token = user_or_patient_instance.generate_refresh_token()
        return (
            True,
            jsonify(
                {
                    "message": "Logged in successfully",
                    "user": user_or_patient_instance.to_dict(),
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                }
            ),
        )
    else:
        return False, jsonify({"message": "Invalid credentials"}), 401


@auth_bp.route("/api/v1/logout", methods=["POST"])
@jwt_required()
def logout():
    access_jti = get_jwt()["jti"]
    db.session.add(TokenBlockList(jti=access_jti))

    refresh_token = request.json.get("refresh_token", None)
    if refresh_token:
        refresh_jti = decode_token(refresh_token)["jti"]
        db.session.add(TokenBlockList(jti=refresh_jti))
    else:
        abort(400, description="Refresh token is missing")

    db.session.commit()
    return jsonify({"message": "Logged out successfully"}), 200


# api forgot password
@auth_bp.route("/api/v1/forgot-password", methods=["GET"], strict_slashes=False)
def forgot_password():
    # TODO implement service to send code to their phone number to use in reseting password
    return (
        jsonify(
            {
                "message": "Please provide your phone number to reset your password",
                "parameters": {"phone_no": "phone number"},
            }
        ),
        200,
    )


# incomplete, need a sms service to send code to their phone number to use in reseting password
@auth_bp.route("/api/v1/forgot-password", methods=["POST"], strict_slashes=False)
def forgot_password_post():
    data = request.get_json()
    phone_no = data.get("phone_no")

    if not phone_no or not is_valid_kenyan_phone(phone_no):
        return jsonify({"message": "Please provide a valid Kenyan phone number"}), 400

    person = Person.query.filter_by(phone_no=phone_no).first()

    if not person:
        return jsonify({"message": "User not found"}), 404

    # TODO implement service to send code to their phone number to use in reseting password
    return (
        jsonify(
            {
                "message": "Please provide the code sent to your phone number and your new password",
                "parameters": {"code": "code", "password": "password"},
            }
        ),
        200,
    )


# api reset password
@auth_bp.route("/api/v1/reset-password", methods=["POST"], strict_slashes=False)
def reset_password():
    """Reset password.
    Requires: (phone_no, code, password, confirm_password)
    """
    data = request.get_json()
    phone_no = data.get("phone_no")
    code = data.get("code")
    password = data.get("password")
    password_confirm = data.get("password_confirm")

    if not code:
        return (
            jsonify({"message": "Please provide the code sent to your phone number"}),
            400,
        )

    if not password or not is_valid_password(password):
        return jsonify({"message": "Please provide valid password"}), 400

    if (
        not password_confirm
        or not is_valid_password(password_confirm)
        or password != password_confirm
    ):
        return jsonify({"message": "Passwords must match"}), 400

    if not phone_no or not is_valid_kenyan_phone(phone_no):
        return jsonify({"message": "Please provide a valid Kenyan phone number"}), 400

    user_or_patient_instance = None
    person = Person.query.filter_by(phone_no=phone_no).first()
    if not person:
        return jsonify({"message": "User not found"}), 404

    if person.type == "user":
        user_or_patient_instance = User.query.filter_by(phone_no=phone_no).first()
    elif person.type == "patient":
        user_or_patient_instance = Patient.query.filter_by(phone_no=phone_no).first()

    new_password_hash = person.set_password(password)

    if user_or_patient_instance:
        user_or_patient_instance.password_hash = new_password_hash
    db.session.commit()

    return jsonify({"message": "Password reset successfully"}), 200


# api change password - same as reset password

# api change phone number- requires an admin to approve the change
@auth_bp.route("/api/v1/change-phone-number", methods=["POST"], strict_slashes=False)
@jwt_required()
def change_phone_number():
    """Change phone number.
    Requires: (phone_no, password)
    """
    data = request.get_json()
    phone_no = data.get("phone_no")
    password = data.get("password")
    new_phone_no = data.get("new_phone_no")

    if not phone_no or not is_valid_kenyan_phone(phone_no):
        return jsonify({"message": "Please provide a valid Kenyan phone number"}), 400

    if not password or not is_valid_password(password):
        return jsonify({"message": "Please provide valid password."}), 400

    person = Person.query.filter_by(phone_no=phone_no).first()

    if not person:
        return jsonify({"message": "User not found"}), 404

    if not person.check_password(password):
        return jsonify({"message": "Invalid credentials"}), 401

    if new_phone_no and not is_valid_kenyan_phone(new_phone_no):
        return jsonify({"message": "Please provide a valid Kenyan phone number"}), 400

    if new_phone_no == phone_no:
        return (
            jsonify({"message": "New phone number cannot be the same as the old one"}),
            400,
        )

    if new_phone_no and Person.query.filter_by(phone_no=new_phone_no).first():
        return jsonify({"message": "Phone number already exists"}), 400

    # TODO implement service to send code to their new number to use in confirming the change

    person.phone_no = new_phone_no
    db.session.commit()
    return jsonify({"message": "Phone number changed successfully"}), 200


# api register - in user's endpoints


# web login
# web logout
# web refresh token

# web register

# web forgot password

# web reset password

# web change password

# web change phone number
