"""Present pregnancy model."""

from app import db

class PresentPregnancy(db.Model):
    """Present pregnancy model."""

    __tablename__ = "present_pregnancies"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    patient = db.relationship(
        "Patient",
        backref=db.backref(
            "present_pregnancy",
            lazy=True
        )
    )

    number_of_contacts = db.Column(db.Integer, nullable=False) # probably should be self incrementing
    date = db.Column(db.Date, nullable=False)
    urine = db.Column(db.String)
    muac = db.Column(db.Float)
    blood_pressure_systolic = db.Column(db.Integer)
    blood_pressure_diastolic = db.Column(db.Integer)
    hemoglobin = db.Column(db.Float)
    pallor = db.Column(db.Boolean)
    gestation_in_weeks = db.Column(db.Integer)
    fundal_height = db.Column(db.Float)
    presentation = db.Column(db.String)
    lie = db.Column(db.String)
    fetal_heart_rate = db.Column(db.Integer)
    fetal_movement = db.Column(db.String)
    next_visit_date = db.Column(db.Date)
