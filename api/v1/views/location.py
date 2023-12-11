"""Location-related endpoints."""

from flask import jsonify, request, abort

from app import db
from api.v1.views import api_bp
from models.location import Location, Tag

from auth.validators import (
    valid_location,
    valid_tag_hierarchy,
    location_exists,
    valid_tag,
)


@api_bp.route("/locations", methods=["POST"], strict_slashes=False)
def create_location():
    """Creates a location."""
    data = request.get_json()
    if not data:
        abort(400, "No input data provided")

    if not valid_location(data):
        abort(400, "Location must have name and tag.")

    location_name = data["name"].lower()

    # check that the tag is valid
    tag = None
    if not valid_tag(data["tag"]):
        abort(400, "Invalid tag provided.")

    tag = db.session.query(Tag).filter_by(name=data["tag"].lower()).first()

    # check that if it has a parent
    parent = None
    if data.get("parent_id"):
        parent = db.session.query(Location).filter_by(id=data["parent_id"]).first()
        if not parent:
            # abort(400, "Parent location does not exist.")
            pass
        if parent and parent.tag.name == data["tag"]:
            abort(400, "Parent location cannot be of the same tag.")
        if parent and not valid_tag_hierarchy(parent.tag.name, data["tag"]):
            abort(400, "Parent location must be higher in the hierachy.")

    if location_exists(location_name, parent):
        abort(400, "Location already exists.")

    location = Location(
        name=data["name"].lower(), tag=tag, parent_id=parent.id if parent else None
    )

    db.session.add(location)
    db.session.commit()
    return (
        jsonify(
            {
                "message": "Location created successfully.",
                "location": location.to_dict(),
            }
        ),
        201,
    )


@api_bp.route("/locations", methods=["GET"], strict_slashes=False)
def get_locations():
    """Get all locations."""
    locations = db.session.query(Location).all()
    return (
        jsonify(
            {
                "message": "Locations retrieved successfully.",
                "locations": [location.to_dict() for location in locations],
            }
        ),
        200,
    )


@api_bp.route(
    "/locations/tags/<string:tag_name>", methods=["GET"], strict_slashes=False
)
def get_locations_by_tag(tag_name):
    """Get all locations by tag."""
    tag = db.session.query(Tag).filter_by(name=tag_name.lower()).first()
    if not tag:
        abort(404, "Tag does not exist.")

    locations = db.session.query(Location).filter_by(tag=tag).all()
    return (
        jsonify(
            {
                "message": "Locations retrieved successfully.",
                "locations": [location.to_dict() for location in locations],
            }
        ),
        200,
    )


@api_bp.route(
    "/locations/tags/<string:tag_name>/<string:location_name>",
    methods=["GET"],
    strict_slashes=False,
)
def get_location_by_tag_and_name(tag_name, location_name):
    """Get a location by tag and name."""
    tag = db.session.query(Tag).filter_by(name=tag_name.lower()).first()
    if not tag:
        abort(404, "Tag does not exist.")

    location = (
        db.session.query(Location)
        .filter_by(name=location_name.lower(), tag=tag)
        .first()
    )
    if not location:
        abort(404, "Location does not exist.")

    return (
        jsonify(
            {
                "message": "Location retrieved successfully.",
                "location": location.to_dict(),
            }
        ),
        200,
    )
