"""module to handle appointments."""

from datetime import datetime
from app import db
from models.person import Person
from models.patient import Patient
from models.user import User
from models.visit import Visit
from models.role import Role


time = "%Y-%m-%dT%H:%M:%S"


class Appointment(db.Model):
    """Define the appointment class."""

    __tablename__ = "appointments"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    #visit_id = db.Column(db.Integer, db.ForeignKey("visits.id"), nullable=False)
    appointment_date = db.Column(db.DateTime, nullable=False)
    appointment_type = db.Column(db.String(128), nullable=False)
    appointment_status = db.Column(db.String(128), nullable=False)

    def __init__(self, *args, **kwargs):
        """Initialize the appointment class."""

        for key, value in kwargs.items():
            if key in ["patient_id", "user_id"]:
                model = Patient if key == "patient_id" else User
                instance = db.session.get(model, value)
                if instance is not None:
                    setattr(self, key, instance.id)
                else:
                    raise ValueError(f"Cannot find {model.__name__} with that id")
                
            if key == "appointment_date":
                try:
                    setattr(self, key, datetime.strptime(value, time))
                except ValueError:
                    raise ValueError(f"Invalid date format. Should be {time}")

            elif key != '__class__':
                setattr(self, key, value)

    def __repr__(self):
        """Represent the appointment class as a string."""
        return "<Appointment: {}>".format(self.id)
    
    def to_dict(self):
        """Return a dictionary representation of an appointment instance."""
        new_dict = {}
        new_dict["__class__"] = self.__class__.__name__
        if "_sa_instance_state" in new_dict:
            del new_dict["_sa_instance_state"]
        return {
            **new_dict,
            "id": self.id,
            "patient_id": self.patient_id,
            "user_id": self.user_id,
            #"visit_id": self.visit_id,
            "appointment_date": self.appointment_date,
            "appointment_type": self.appointment_type,
            "appointment_status": self.appointment_status
        }
    
    def save(self):
        """Save an appointment."""
        db.session.add(self)
        db.session.commit()

    def update_status(self, status):
        """Update the status of an appointment."""
        self.appointment_status = status
        db.session.commit()

    def reschedule(self, new_date):
        """Reschedule an appointment."""
        self.appointment_date = new_date
        db.session.commit()
