"""Clinical Note Model."""

from app import db


class ClinicalNote(db.Model):
    """Clinical Note Model."""

    __tablename__ = 'clinical_notes'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    patient = db.relationship(
        "Patient",
        backref=db.backref(
            "clinical_notes",
            lazy=True
        )
    )
    # appointment_id = Column(Integer, ForeignKey('appointments.id'), nullable=False)
    # appointment = db.relationship("Appointment", backref="clinical_notes")
    date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text)
    next_visit_date = db.Column(db.Date)


    def to_dict(self):
        """Return dictionary representation of the clinical note model."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
