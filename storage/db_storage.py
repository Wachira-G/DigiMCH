"""Database storage engine module."""

class DbStorage:
    """Database storage engine class."""
    db = None

    def __init__(self, db):
        """Initialize the database storage engine."""
        self.db = db

    def all(self, cls=None) -> list:
        """Return all objects of a given class."""
        return self.db.session.query(cls).all()

    def new(self, obj):
        """Add a new object to the database."""
        self.db.session.add(obj)

    def save(self):
        """Save changes to the database."""
        self.db.session.commit()

    def delete(self, obj=None):
        """Delete an object from the database."""
        if obj is not None:
            self.db.session.delete(obj)

    def reload(self):
        """Create all tables in the database."""
        self.db.create_all()

    def close(self):
        """Close the database session."""
        self.db.session.close()

    def get(self, cls, id):
        """Get an object from the database."""
        return self.db.session.query(cls).get(id)

    def count(self, cls=None):
        """Count the number of objects in storage."""
        session = Session(self.db)
        if cls is None:
            return session.query(cls).count()
        else:
            return session.query(cls).count()
            return self.db.session.query(cls).count()