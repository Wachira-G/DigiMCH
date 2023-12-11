from app import db


class Tag(db.Model):
    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(
        db.String(255), nullable=False, unique=True
    )  # e.g., county, subcounty, location
    parent_id = db.Column(db.Integer, db.ForeignKey("tags.id"), nullable=True)

    parent = db.relationship("Tag", remote_side=[id])

    def to_dict(self) -> dict:
        """Return a dictionary representation of the tag."""
        return {"id": self.id, "name": self.name, "parent": self.parent_id}


class Location(db.Model):
    __tablename__ = "locations"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey("locations.id"))

    tag_id = db.Column(db.Integer, db.ForeignKey("tags.id"), nullable=False)
    tag = db.relationship("Tag")

    __table_args__ = (
        db.UniqueConstraint("name", "parent_id", name="unique_location_within_parent"),
    )

    def to_dict(self) -> dict:
        """Return a dictionary representation of the location."""
        parent = db.session.query(Location).filter_by(id=self.parent_id).first()
        return {
            "id": self.id,
            "name": self.name.capitalize(),
            "parent": parent.name.capitalize() if parent else None,
            "tag": self.tag.to_dict() if self.tag else None,
        }
