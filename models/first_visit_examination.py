"""Phyical Examination during the first visit model."""

from app import db


class PhysicalExaminationFirstVisit(db.Model):
    """First visit examination model."""

    __tablename__ = "physical_examinations_first_visit"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    patient = db.relationship(
        "Patient",
        backref=db.backref(
            "physical_examinations_first_visit",
            lazy=True,
            uselist=False
        )
    )

    general_examination = db.Column(db.Text)

    blood_pressure_systolic = db.Column(db.Integer)
    blood_pressure_diastolic = db.Column(db.Integer)
    pulse_rate = db.Column(db.Integer)
    cardiovascular_system = db.Column(db.Text)
    respiratory_system = db.Column(db.Text)

    abdomen = db.Column(db.Text)
    breasts = db.Column(db.Text)

    external_genitalia_examination = db.Column(db.Text)
    discharge_present = db.Column(db.Boolean)
    discharge_characteristics = db.Column(db.Text, nullable=True)
    genital_ulcer_present = db.Column(db.Boolean)
    genital_ulcer_characteristics = db.Column(db.Text, nullable=True)


    def to_dict(self):
        """Return the first visit examination as a dictionary."""
        fields = {
            "patient_id": self.patient_id,
            "general_examination": self.general_examination,
            "blood_pressure_systolic": self.blood_pressure_systolic,
            "blood_pressure_diastolic": self.blood_pressure_diastolic,
            "pulse_rate": self.pulse_rate,
            "cardiovascular_system": self.cardiovascular_system,
            "respiratory_system": self.respiratory_system,
            "abdomen": self.abdomen,
            "breasts": self.breasts,
            "external_genitalia_examination": self.external_genitalia_examination,
            "discharge_present": self.discharge_present,
            "discharge_characteristics": self.discharge_characteristics,
            "genital_ulcer_present": self.genital_ulcer_present,
            "genital_ulcer_characteristics": self.genital_ulcer_characteristics,
        }
        return fields


    def save(self):
        """Save the first visit examination to the database."""
        db.session.add(self)
        db.session.commit()

    def update(self, data):
        """Update a first visit examination instance."""
        for key, item in data.items():
            if key not in ["patient_id"]:
                setattr(self, key, item)
        db.session.commit()
