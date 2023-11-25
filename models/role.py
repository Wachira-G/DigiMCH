
"""Module for Role model."""

import uuid
from app import db


person_role = db.Table(
    "person_role",
    db.Column("person_id", db.String(60), db.ForeignKey("persons.id")),
    db.Column("role_id", db.String(60), db.ForeignKey("roles.id")),
)


class Role(db.Model):
    """Role model class."""

    __tablename__ = "roles"

    id = db.Column(db.String(60), primary_key=True)
    name = db.Column(db.String(128), nullable=False)

    persons = db.relationship("Person", secondary=person_role, back_populates="roles")

    def __init__(self, name: str):
        """Initialize a Role object."""
        self.name = name
        self.id = str(uuid.uuid4())

    def __repr__(self):
        return f"<Role {self.name}>"
    
    def to_dict(self):
        """Return a dictionary representation of a Role object."""
        return {
            "id": self.id,
            "name": self.name,
        }