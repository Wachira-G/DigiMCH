"""Maternal profile class."""

from datetime import timedelta, datetime
from app import db


class MaternalProfile(db.Model):
    """Class to record the maternal profile of a patient."""
    __tablename__ = "maternal_profiles"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    patient = db.relationship(
        "Patient",
        backref=db.backref(
            "maternal_profile",
            lazy=True,
            uselist=False
        )
    )

    # age = db.Column()  # link to patient's birth_date
    gravida = db.Column(db.Integer) # number of pregnancies
    parity = db.Column(db.Integer) # number of deliveries
    para = db.Column(db.Integer) # number of viable births
    height = db.Column(db.Float)
    weight = db.Column(db.Float)
    lmp = db.Column(db.DateTime)
    # EDD = db.Column(db.DateTime) # estimated date of delivery calculated from LMP assuming 40 weeks gestation as default

    @property 
    def age(self):
        """Return age of patient."""
        if self.patient is not None:
            age = (datetime.now().date() - self.patient.birth_date.date()).days / 365
            return age
        return None
    
    @property
    def edd(self):
        """Estimatd Date of Delivery Calculated from LMP assuming 40 weeks gestation as default."""
        if self.lmp is not None:
            return self.lmp + timedelta(weeks=40)
        return None
    
    def to_dict(self):
        """Return dictionary representation of the maternal profile model."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
