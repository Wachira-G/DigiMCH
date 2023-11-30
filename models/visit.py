"""Module for visit model."""

from app import db
from datetime import datetime
from models.patient import Patient
from models.user import User


class Visit(db.Model):
    """Visit class."""

    __tablename__ = "visits"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_datetime = db.Column(db.DateTime, nullable=False)
    end_datetime = db.Column(db.DateTime)
    visit_type = db.Column(db.String(128), nullable=True)
    #  (e.g., routine check-up, emergency, follow-up).
    encounters = db.relationship('Encounter', backref='visit', lazy=True)

    def __init__(self, start_datetime=datetime.now(), *args, **kwargs):
        """Initialize a visit instance."""
        self.start_datetime = start_datetime

        for key, value in kwargs.items():
            if key in ["patient_id", "user_id"]:
                model = Patient if key == "patient_id" else User
                instance = db.session.get(model, value)
                if instance is not None:
                    setattr(self, key, instance.id)
                else:
                    raise ValueError(f"Cannot find {model.__name__} with that id")

            elif key != '__class__':
                setattr(self, key, value)

    def end_visit(self, end_datetime=datetime.now()):
        """End a visit."""
        self.end_datetime = end_datetime

    def to_dict(self):
        """Return a dictionary representation of a visit instance."""
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "user_id": self.user_id,
            "start_datetime": self.start_datetime,
            "end_datetime": self.end_datetime,
            "visit_type": self.visit_type
        }

    def __repr__(self):
        """Return a string representation of a visit instance."""
        return f"<Visit: {self.id}>"
