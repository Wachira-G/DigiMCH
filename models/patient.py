"""Define the patient module."""

import uuid
import datetime
from models.person import Person, Base
from storage.db_storage import DbStorage as storage
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from app import db


class Patient(Person, db.Model, Base):
    """patient class."""
    __tablename__ = 'patients'
    role_id = Column(String(128) )#, ForeignKey('roles.id'))
    wcw_no = Column(String(128), nullable=True)
    patient_no = Column(String(128), nullable=True)
    sys_gen_uniq_no = Column(String(128), nullable=True)
    #patient_type = Column(String(128), nullable=True)
    alt_phone_no = Column(String(128), nullable=True)
    marital_status = Column(String(128), nullable=True)
    telephone = Column(String(128), nullable=True)
    education_level = Column(String(128), nullable=True)
    next_of_kin = Column(String(128), nullable=True)
    next_of_kin_relationship = Column(String(128), nullable=True)
    next_of_kin_contacts = Column(String(128), nullable=True)
