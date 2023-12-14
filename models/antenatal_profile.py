"""Antenatal profile module."""

from app import db


class AntenatalProfile(db.Model):
    __tablename__ = 'antenatal_profile'

    id = db.Column(db.Integer, primary_key=True)
    # appointment = db.relationship("Appointment", backref="antenatal_profile_mch_focused")
    # appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'))
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    patient = db.relationship(
        "Patient",
        backref=db.backref(
            "antenatal_profile",
            lazy=True,
            uselist=False
        )
    )                                       

    # Antenatal profile
    hemoglobin = db.Column(db.Float)
    blood_group = db.Column(db.String)
    rhesus = db.Column(db.String)
    urinalysis = db.Column(db.Text)
    blood_rbs = db.Column(db.Float)
    tb_screening_tool = db.Column(db.Boolean)
    tb_screening_outcome = db.Column(db.Text)
    isoniazid_preventive_therapy = db.Column(db.Boolean)
    ipt_given_date = db.Column(db.Date)
    next_visit_date = db.Column(db.Date)

    # Obstetric ultrasound
    obstetric_ultrasound_first_done = db.Column(db.Boolean)
    first_ultrasound_gestation = db.Column(db.Integer)
    first_ultrasound_date = db.Column(db.Date)
    obstetric_ultrasound_second_done = db.Column(db.Boolean)
    second_ultrasound_gestation = db.Column(db.Integer)
    second_ultrasound_date = db.Column(db.Date)

    # Triple Test
    triple_testing_date = db.Column(db.Date)
    hiv_test_result = db.Column(db.Text)
    syphilis_test_result = db.Column(db.Text)
    hepatitis_b_test_result = db.Column(db.Text)
    hiv_non_reactive_retesting_date = db.Column(db.Date)

    # Couple HIV testing
    couple_hiv_counseling_done = db.Column(db.Boolean)
    partner_hiv_status = db.Column(db.Text)

    def to_dict(self):
        """Return dictionary representation of the antenatal profile model."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
