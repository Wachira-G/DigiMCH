
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from app import db

Base = declarative_base()
storage = db
time = "%Y-%m-%dT%H:%M:%S.%f"


class Person():
    """Define a basic person."""
    id = Column(String(60), primary_key=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    first_name = Column(String(128), nullable=True)
    surname = Column(String(128), nullable=True)
    middle_name = Column(String(128), nullable=True)
    phone_no = Column(String(128), nullable=True)
    location_id = Column(String(128), nullable=True)
    sex = Column(String(128), nullable=True)
    birth_date = Column(DateTime, nullable=True)
    username = Column(String(128), nullable=True)
    password_hash = Column(String(128), nullable=True)
    # role_id = ""


    def __init__(self, *args, **kwargs):
        """Initialize a basic person."""
        if kwargs:
            for key, value in kwargs.items():
                if key in ["updated_at", "created_at", "birth_date"]:
                    setattr(
                            self,
                            key,
                            datetime.strptime(
                              value, "%Y-%m-%dT%H:%M:%S.%f"),
                            )
                else:
                    if key != "__class__":
                        setattr(self, key, value)

            if "id" not in kwargs.keys():
                self.id = str(uuid.uuid4())
                self.created_at = datetime.now()
                self.updated_at = self.created_at

    def __str__(self):
        """print representation of person object."""
        return str(self.__dict__)

    def to_dict(self, save_fs=None):
        """returns a dictionary containing all keys/values of the instance"""
        new_dict = self.__dict__.copy()
        if "created_at" in new_dict:
            new_dict["created_at"] = new_dict["created_at"].strftime(time)
        if "updated_at" in new_dict:
            new_dict["updated_at"] = new_dict["updated_at"].strftime(time)
        new_dict["__class__"] = self.__class__.__name__
        if "_sa_instance_state" in new_dict:
            del new_dict["_sa_instance_state"]
        if save_fs is None:
            if "password" in new_dict:
                del new_dict["password"]
        return new_dict
    
    def save(self):
        """Save a person to the database."""
        storage.new(self)
        storage.save()

    def delete(self):
        """Delete a person from the database."""
        storage.delete(self)
        storage.save()

    def update(self, **kwargs):
        """Update a person."""
        for key, value in kwargs.items():
            if key not in ["id", "created_at", "updated_at"]:
                setattr(self, key, value)
        self.updated_at = datetime.now()
        storage.save()
