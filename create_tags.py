"""Create tags."""

from app import db
from auth.validators import TAGS_HIERARCHY
from models.location import Tag

def create_tags(TAGS_HIERARCHY=TAGS_HIERARCHY):
    """"Establish tags."""
    for index in range(len(TAGS_HIERARCHY)):
        tag_name = TAGS_HIERARCHY[index].lower()
        exists = db.session.query(Tag).filter_by(name=tag_name).first()
        if exists:
            continue
        tag_parent = None
        if index:
            tag_parent = get_tag(TAGS_HIERARCHY[index - 1])
        tag_object = Tag(name=tag_name, parent_id=tag_parent.id if tag_parent else None)
        db.session.add(tag_object)
        db.session.commit()

def get_tag(tag_name):
    """Get tag object."""
    tag = db.session.query(Tag).filter_by(name=tag_name).first()
    return tag
