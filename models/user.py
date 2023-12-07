"""User module to handle persons with admin and user roles."""

from models.person import Person
from app import db


class User(Person):
    """Define user."""

    __tablename__ = "users"

    id = db.Column(db.String(60), db.ForeignKey("persons.id"), primary_key=True)
    facility_id = db.Column(db.String(128), nullable=False)
    kmpdu_no = db.Column(db.String(128), nullable=True)

    __mapper_args__ = {
         'polymorphic_identity':'user',
    }

    def to_dict(self):
        self_dict = {"facility_id": self.facility_id, "kmpdu_no": self.kmpdu_no}
        return {**super().to_dict(), **self_dict}
