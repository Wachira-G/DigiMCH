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

    #__mapper_args__ = {
    #    'polymorphic_identity':'patient',
    #}

    #def __init__(self, *args, **kwargs):
    #    super().__init__(*args, **kwargs)
    #    self.type = 'user'