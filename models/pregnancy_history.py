"""Module for the PregnancyHistory class."""


from app import db


class PregnancyHistory(db.Model):
    """Model for the pregnancy history of the patient."""

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pregnancy_order = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    number_of_anc_attended = db.Column(db.Integer)
    place_of_childbirth = db.Column(
        db.String(255)
    )  # can be home, hospital, clinic, etc. TODO link to location model
    gestation_in_weeks = db.Column(db.Float)
    duration_of_labour_hours = db.Column(db.Integer)
    mode_of_delivery = db.Column(db.String(255))
    birth_weight_grams = db.Column(db.Integer)
    sex = db.Column(db.String())  # M or F
    outcome = db.Column(db.String(255))
    puerperium = db.Column(db.String(255))

    # Relationships
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    patient = db.relationship(
        "Patient", backref=db.backref("pregnancy_history", lazy=True)
    )

    def to_dict(self):
        """Return the pregnancy history as a dictionary."""
        fields = {
            "patient_id": self.patient_id,
            "pregnancy_order": self.pregnancy_order,
            "year": self.year,
            "number_of_anc_attended": self.number_of_anc_attended,
            "place_of_childbirth": self.place_of_childbirth,
            "gestation_in_weeks": self.gestation_in_weeks,
            "duration_of_labour_hours": self.duration_of_labour_hours,
            "mode_of_delivery": self.mode_of_delivery,
            "birth_weight_grams": self.birth_weight_grams,
            "sex": self.sex,
            "outcome": self.outcome,
            "puerperium": self.puerperium,
        }
        return fields

    def update(self, data):
        """Update a Pregnancy history instance."""
        for key, item in data.items():
            if key not in ["patient_id"]:
                setattr(self, key, item)
        db.session.commit()
