"""Medical History Model"""


from app import db


class MedicalHistory(db.Model):
    """Model for the medical history of the patient."""

    __tablename__ = "medical_history"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    patient = db.relationship(
        "Patient", backref=db.backref("medical_history", lazy=True, uselist=False)
    )

    # Surgical history
    surgical_operation = db.Column(db.String(255))

    # Diabetes
    diabetes = db.Column(db.Boolean, nullable=False)

    # Hypertension
    hypertension = db.Column(db.Boolean, nullable=False)

    # Blood transfusion
    blood_transfusion = db.Column(db.Boolean, nullable=False)

    # Tuberculosis
    tuberculosis = db.Column(db.Boolean, nullable=False)

    # Drug allergies
    drug_allergy = db.Column(db.Boolean, nullable=False)
    drug_allergy_details = db.Column(db.String(255), nullable=True)

    # Other allergies
    other_allergies = db.Column(db.String(255), nullable=True)

    # Family history
    family_history_twins = db.Column(db.Boolean, nullable=False)
    family_history_tuberculosis = db.Column(db.Boolean, nullable=False)

    def to_dict(self):
        """Return the medical history as a dictionary."""
        fields = {
            "patient_id": self.patient_id,
            "surgical_operation": self.surgical_operation,
            "diabetes": self.diabetes,
            "hypertension": self.hypertension,
            "blood_transfusion": self.blood_transfusion,
            "tuberculosis": self.tuberculosis,
            "drug_allergy": self.drug_allergy,
            "drug_allergy_details": self.drug_allergy_details,
            "other_allergies": self.other_allergies,
            "family_history_twins": self.family_history_twins,
            "family_history_tuberculosis": self.family_history_tuberculosis,
        }
        return fields

    def update(self, data):
        """Update a Medical history instance."""
        for key, item in data.items():
            if key not in ["patient_id"]:
                setattr(self, key, item)
        db.session.commit()
