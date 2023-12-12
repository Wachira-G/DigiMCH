"""Module for Role model."""

from marshmallow import Schema, fields
from app import db

person_role = db.Table(
    "person_role",
    db.Column("person_id", db.Integer, db.ForeignKey("persons.id")),
    db.Column("role_id", db.Integer, db.ForeignKey("roles.id")),
)

class RoleSchema(Schema):
    """Schema for the Role model."""

    id = fields.Int(dump_only=True)
    name = fields.Str()
    role_description = fields.Str()


class Role(db.Model):
    """Role model class."""

    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), nullable=False)
    role_description = db.Column(db.String(128), nullable=True)

    # person_id = db.Column(db.Integer, db.ForeignKey("persons.id"))
    person = db.relationship("Person", secondary=person_role, back_populates="roles")

    def __init__(self, name: str, role_description: str = None, *args, **kwargs):
        """Initialize a Role object."""
        self.name = name
        self.role_description = role_description

    def __repr__(self):
        return f"<Role {self.name}>"

    def to_dict(self):
        """Return a dictionary representation of a Role object."""
        return {
            "id": self.id,
            "name": self.name,
            "role_description": self.role_description,
        }
