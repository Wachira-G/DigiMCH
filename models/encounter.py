"""Module to define the encouter model."""

from datetime import datetime
from app import db
from models.visit import Visit
from models.patient import Patient
from models.user import User


class Encounter(db.Model):
    """Encounter class."""

    __tablename__ = "encounters"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    visit_id = db.Column(db.Integer, db.ForeignKey('visits.id'), nullable=False)
    encounter_type = db.Column(db.String(128), nullable=False)
    # e.g (triage, lab, pharmacy, inpatient, imaging, doctors-consultation, etc)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_datetime = db.Column(db.DateTime, nullable=False)
    end_datetime = db.Column(db.DateTime)
    # encounter_status = db.Column(db.String(128), nullable=False)
    # (e.g., in-progress, completed, cancelled).
    # encounter_outcome = db.Column(db.String(128), nullable=False)
    # (e.g., treated, referred, admitted, etc).
    # encounter_notes = db.Column(db.String(128), nullable=False)
    # (e.g., treated, referred, admitted, etc).

    def __init__(self, *args, **kwargs):
        """Initialize an encounter instance."""
        self.start_datetime = datetime.now()

        for key, value in kwargs.items():
            if key in ["visit_id", "patient_id", "user_id"]:
                model = Visit if key == "visit_id" else Patient if key == "patient_id" else User
                instance = db.session.get(model, value)
                if instance is not None:
                    setattr(self, key, instance.id)
                else:
                    raise ValueError(f"Cannot find {model.__name__} with that id")

            elif key != '__class__':
                setattr(self, key, value)

    def end_encounter(self, end_datetime=datetime.now()):
        """End an encounter."""
        self.end_datetime = end_datetime

    def to_dict(self):
        """Return a dictionary representation of an encounter instance."""
        return {
            "id": self.id,
            "visit_id": self.visit_id,
            "patient_id": self.patient_id,
            "user_id": self.user_id,
            "start_datetime": self.start_datetime,
            "end_datetime": self.end_datetime,
            "encounter_type": self.encounter_type
        }
    
    def __repr__(self):
        """Return a string representation of an encounter instance."""
        return f"<Encounter: {self.id}>"
