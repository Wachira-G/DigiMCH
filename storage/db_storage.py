
from flask_sqlalchemy import SQLAlchemy
"""Database storage engine module."""


class DbStorage:
    """Database storage engine class.

    Attributes:
        db (SQLAlchemy): The SQLAlchemy instance.
    """
    db = None

    def __init__(self, db: SQLAlchemy):
        """Initialize the database storage engine.

        Args:
            db (SQLAlchemy): A SQLAlchemy instance.
        """
        if db is None:
            self.db = None
        else:
            self.db = db

    def all(self, cls=None) -> list:
        """Return all objects of a given class.

        Args:
            cls (type, optional): The class to query. Defaults to None.

        Returns:
            list: A list of objects.
        """
        if self.db is None:
            return []
        else:
            return self.db.session.query(cls).all()

    def new(self, obj):
        """Add a new object to the database.

        Args:
            obj: The object to add.
        """
        if self.db is not None:
            self.db.session.add(obj)

    def save(self):
        """Save changes to the database."""
        if self.db is not None:
            self.db.session.commit()

    def delete(self, obj=None):
        """Delete an object from the database.

        Args:
            obj: The object to delete.
        """
        if self.db is not None and obj is not None:
            self.db.session.delete(obj)

    def reload(self):
        """Create all tables in the database."""
        if self.db is not None:
            self.db.create_all()

    def close(self):
        """Close the database session."""
        if self.db is not None:
            self.db.session.close()

    def get(self, cls, id) -> object:
        """Get an object from the database.

        Args:
            cls (type): The class of the object.
            id: The ID of the object.

        Returns:
            object: The object with the specified ID.
        """
        if self.db is None:
            return None
        else:
            return self.db.session.query(cls).get(id)

    def count(self, cls=None) -> int:
        """Count the number of objects in storage.

        Args:
            cls (type, optional): The class to count. Defaults to None.

        Returns:
            int: The number of objects.
        """
        if self.db is None:
            return 0
        else:
            return self.db.session.query(cls).count()