from models.person import Person, Base
from app import db
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship


class Provider(Person, db.Model, Base):
    role_id = Column(String(128))  # , ForeignKey('roles.id'))
    facility_id = Column(String(128), nullable=True)
    kmpdu_no = Column(String(128), nullable=True)