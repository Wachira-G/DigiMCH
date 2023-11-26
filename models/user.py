"""USer module to handle persons with admin and user roles."""

from models.person import Person
from app import db


class User(Person):
    """Define user."""

    __tablename__ = "users"

    id = db.Column(db.String(60), db.ForeignKey("persons.id"), primary_key=True)
    facility_id = db.Column(db.String(128), nullable=False)
    kmpdu_no = db.Column(db.String(128), nullable=True)
