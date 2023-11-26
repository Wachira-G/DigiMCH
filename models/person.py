import uuid
from datetime import datetime
from flask import current_app
from app import db
from itsdangerous import BadSignature, SignatureExpired, Serializer
import hashlib
from models.role import person_role

storage = db
time = "%Y-%m-%dT%H:%M:%S.%f"


class Person(db.Model):
    """Define a basic person."""

    __tablename__ = "persons"

    id = db.Column(db.String(60), primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)

    first_name = db.Column(db.String(128), nullable=False)
    surname = db.Column(db.String(128), nullable=True)
    middle_name = db.Column(db.String(128), nullable=True)
    phone_no = db.Column(db.String(128), nullable=False)
    location_id = db.Column(db.String(128), nullable=True)
    sex = db.Column(db.String(128), nullable=False)
    birth_date = db.Column(db.DateTime, nullable=False)
    password_hash = db.Column(db.String(128), nullable=True)

    roles = db.relationship("Role", secondary=person_role, back_populates="persons")

    def __init__(self, *args, **kwargs):
        """Initialize a basic person."""
        if kwargs:
            for key, value in kwargs.items():
                if key in ["updated_at", "created_at", "birth_date"]:
                    setattr(self, key, datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f"))
                else:
                    if "password" in key:
                        setattr(self, "password_hash", self.generate_hash(value))
                    if key != "__class__":
                        setattr(self, key, value)

            if "id" not in kwargs.keys():
                self.id = str(uuid.uuid4())
                self.created_at = datetime.now()
                self.updated_at = self.created_at

    def __str__(self):
        """print representation of person object."""
        return str(self.__dict__)

    def to_dict(self, save_fs=None):
        """returns a dictionary containing all keys/values of the instance"""
        new_dict = self.__dict__.copy()
        if "created_at" in new_dict:
            new_dict["created_at"] = new_dict["created_at"].strftime(time)
        if "updated_at" in new_dict:
            new_dict["updated_at"] = new_dict["updated_at"].strftime(time)
        new_dict["__class__"] = self.__class__.__name__
        if "_sa_instance_state" in new_dict:
            del new_dict["_sa_instance_state"]
        if save_fs is None:
            if "password" in new_dict:
                del new_dict["password"]
        if self.roles:
            new_dict["roles"] = [role.to_dict() for role in self.roles]
        return new_dict

    def update(self, **kwargs):
        """Update a person."""
        for key, value in kwargs.items():
            if key not in ["id", "created_at", "updated_at"]:
                setattr(self, key, value)
        self.updated_at = datetime.now()
        storage.save()

    def generate_auth_token(self, expiration=600):
        """Generate the auth token."""
        s = Serializer(current_app.config["SECRET_KEY"])
        return s.dumps({"id": self.id})

    @staticmethod
    def verify_auth_token(token, model):
        """Verify the auth token."""
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token)
        except (BadSignature, SignatureExpired):
            return None
        instance = model.query.get(data["id"])
        return instance

    @staticmethod
    def generate_hash(password):
        """Generate a password hash."""
        return hashlib.md5(password.encode()).hexdigest()

    def check_password(self, password):
        """Check if a password matches the hash."""
        return self.password_hash == self.generate_hash(password)

    def set_password(self, password):
        """Set a password."""
        self.password_hash = self.generate_hash(password)
