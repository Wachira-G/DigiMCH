"""Define the patient module."""

from app import db
from models.person import Person


class Patient(Person):
    """patient class."""

    __tablename__ = "patients"

    id = db.Column(db.Integer, db.ForeignKey("persons.id"), primary_key=True)

    wcw_no = db.Column(db.String(128), nullable=True)
    # patient_no = db.Column(db.String(128), nullable=True)
    sys_gen_uniq_no = db.Column(db.String(128), nullable=True)
    alt_phone_no = db.Column(db.String(128), nullable=True)
    marital_status = db.Column(db.String(128), nullable=True)
    telephone = db.Column(db.String(128), nullable=True)
    education_level = db.Column(db.String(128), nullable=True)
    next_of_kin = db.Column(db.String(128), nullable=True)
    next_of_kin_relationship = db.Column(db.String(128), nullable=True)
    next_of_kin_contacts = db.Column(db.String(128), nullable=True)

    __mapper_args__ = {
        'polymorphic_identity':'patient',
    }

    def to_dict(self):
        self_dict = {
            "wcw_no": self.wcw_no,
            "sys_gen_uniq_no": self.sys_gen_uniq_no,
            "alt_phone_no": self.alt_phone_no,
            "marital_status": self.marital_status,
            "telephone": self.telephone,
            "education_level": self.education_level,
            "next_of_kin": self.next_of_kin,
            "next_of_kin_relationship": self.next_of_kin_relationship,
            "next_of_kin_contacts": self.next_of_kin_contacts,
        }
        return {**super().to_dict(), **self_dict}