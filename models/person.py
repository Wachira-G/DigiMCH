from datetime import datetime, timedelta
from flask import current_app
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    decode_token,
)
from flask_login import UserMixin  # TODO will remove this
from itsdangerous import BadSignature, SignatureExpired, TimedSerializer as Serializer
import logging

from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import func
from app import db
from auth.blocklist import TokenBlockList

from models.role import person_role, Role

storage = db
time = "%Y-%m-%dT%H:%M:%S"


class Person(UserMixin, db.Model):
    """Define a basic person."""

    __tablename__ = "persons"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(
        db.DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = db.Column(
        db.DateTime(timezone=True), onupdate=func.now(), nullable=False
    )

    first_name = db.Column(db.String(128), nullable=False)
    surname = db.Column(db.String(128), nullable=False)
    middle_name = db.Column(db.String(128), nullable=True)
    phone_no = db.Column(db.String(128), unique=True, nullable=False)
    location_id = db.Column(db.String(128), nullable=True)
    sex = db.Column(db.String(128), nullable=False)
    birth_date = db.Column(db.DateTime, nullable=False)
    password_hash = db.Column(db.String(512), nullable=False)
    # created_by = db.Column(db.Integer, nullable=False)

    roles = db.relationship("Role", secondary=person_role, back_populates="person")

    type = db.Column(db.String(50))

    __mapper_args__ = {"polymorphic_identity": "person", "polymorphic_on": type}

    def __init__(self, *args, **kwargs):
        """Initialize a basic person."""
        # assign attributes to person for use by to_dict
        self.id = None
        if self.created_at is None:
            self.created_at = datetime.now()
            self.updated_at = self.created_at

        self.first_name = None
        self.surname = None
        self.middle_name = None
        self.phone_no = None
        self.location_id = None
        self.sex = None
        self.birth_date = None
        self.password_hash = None
        self.created_by = None

        if kwargs:
            for key, value in kwargs.items():
                if key == "birth_date":
                    try:
                        setattr(self, key, datetime.strptime(value, time))
                    except ValueError:
                        print(f"Invalid date format for {key}: {value}")

                elif key == "password":
                    setattr(self, "password_hash", self.generate_hash(value))

                elif key == "phone_no":
                    if self.phone_no_exits(value):
                        raise ValueError("Phone number already exists")
                    setattr(self, key, value)

                # save role
                elif key == "role":
                    # find out if person already has role, and skip if they do
                    role = self.get_role(value)
                    self.assign_role(role)

                # save roles
                elif key == "roles":
                    for role_name in value:
                        role = self.get_role(role_name)
                        self.assign_role(role)

                # save other attributes
                elif key != "__class__":
                    setattr(self, key, value)

    def __str__(self):
        """print representation of person object."""
        return str(self.__dict__)

    def to_dict(self):
        """returns a dictionary containing all keys/values of the instance"""
        new_dict = {}
        for attr in [
            "id",
            "created_at",
            "updated_at",
            "first_name",
            "surname",
            "middle_name",
            "phone_no",
            "location_id",
            "sex",
            "birth_date",
        ]:
            value = getattr(self, attr, None)
            if value is not None:
                if isinstance(value, datetime):
                    value = value.strftime(time)
                else:
                    new_dict[attr] = value
        new_dict["__class__"] = self.__class__.__name__
        if "_sa_instance_state" in new_dict:
            del new_dict["_sa_instance_state"]
        if self.roles:
            new_dict["roles"] = [role.to_dict() for role in self.roles]
        return new_dict

    def update(self, **kwargs):
        """Update a person."""
        for key, value in kwargs.items():
            if key not in ["id", "created_at", "updated_at"]:
                setattr(self, key, value)
        self.updated_at = datetime.now()
        storage.session.commit()

    def generate_access_token(self, expiration=60 * 60):
        """Generate the jwt access token."""
        if self.id is None:
            raise ValueError("Cannot generate token: Person instance has no id")
        # s = Serializer(current_app.config["SECRET_KEY"])
        # return s.dumps({"id": self.id}) # simplify token generation TODO: add expiration
        return create_access_token(
            identity=self.id, expires_delta=timedelta(seconds=expiration)
        )

    def generate_refresh_token(self, expiration=60 * 60 * 24):
        """Generated the jwt refresh token."""
        if self.id is None:
            raise ValueError("Cannot generate token: Person instance has no id")
        return create_refresh_token(
            identity=self.id, expires_delta=timedelta(seconds=expiration)
        )

    @staticmethod
    def verify_auth_token(token, model):
        """Verify the auth token."""
        if not token:
            print("Token is None")
            return None
        try:
            if token.startswith("Bearer "):  # strip the bearer prefix
                token = token[7:]
            if TokenBlockList.is_jti_blocklisted(token):
                return None
            data = decode_token(encoded_token=token)
        except Exception as e:
            print(f"Error decoding token: {e}")
            return None
        if "sub" not in data:  # sub = identity
            return None
        instance = model.query.get(data["sub"])
        return instance

    @staticmethod
    def generate_hash(password) -> str:
        """Generate a password hash."""
        return generate_password_hash(password)

    def check_password(self, password) -> bool:
        """Check if a password matches the hash.
        Returns True if it does, False if it doesn't.
        """
        return check_password_hash(self.password_hash, password)

    def set_password(self, password) -> None:
        """Set a password."""
        self.password_hash = self.generate_hash(password)

    def get_role(self, role_name):
        """Get a role."""
        role = None
        if role_name is None or role_name == "":
            return None
        try:
            role = Role.query.filter_by(name=role_name).first()
        except Exception as e:
            logging.error(f"Failed to get role: {e}")
            return None
        finally:
            return role

    def assign_role(self, role):
        """Assign a role to a person."""
        if role is None:
            return
        if role not in self.roles:
            self.roles.append(role)
            storage.session.add(self)
            storage.session.commit()

    def remove_role(self, role):
        """Remove a role from a person."""
        if role in self.roles:
            self.roles.remove(role)
            storage.session.commit()

    def assign_roles(self, roles):
        """Assign roles to a person."""
        for role in roles:
            self.assign_role(role)

    def phone_no_exits(self, phone_no):
        """Check if a phone number exists."""
        person = Person.query.filter_by(phone_no=phone_no).first()
        if person:
            return True
        return False
