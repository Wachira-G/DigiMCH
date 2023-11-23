
""" Provider API """

from api.v1.views import api_bp
from models.provider import Provider
from flask import jsonify, request, abort, current_app


storage = current_app.config['storage']

@api_bp.route('/providers', methods=['GET'], strict_slashes=False)
def get_providers():
    """ Get all providers """
    providers = storage.all(Provider)
    return jsonify([provider.to_dict() for provider in providers])

@api_bp.route('/providers', methods=['POST'], strict_slashes=False)
def create_provider():
    """ Create a provider """
    provider = request.get_json()
    if 'first_name' not in provider:
        abort(400, 'Missing first_name')
    if 'surname' not in provider:
        abort(400, 'Missing surname')
    if 'middle_name' not in provider:
        abort(400, 'Missing middle_name')
    if 'phone_no' not in provider:
        abort(400, 'Missing phone_no')
    # if 'location_id' not in provider:

    provider_obj = Provider(**provider)

    storage.new(provider_obj)
    storage.save()
    return jsonify(provider_obj.to_dict()), 201

@api_bp.route('/providers/<provider_id>', methods=['GET'], strict_slashes=False)
def get_provider(provider_id):
    """ Get a provider """
    provider = storage.get(Provider, provider_id)
    if not provider:
        abort(404)
    return jsonify(provider.to_dict())

@api_bp.route('/providers/<provider_id>', methods=['PUT'], strict_slashes=False)
def update_provider(provider_id):
    """ Update a provider """
    provider = storage.get(Provider, provider_id)
    if not provider:
        abort(404)
    provider_data = request.get_json()
    for key, value in provider_data.items():
        if key not in ['id', 'created_at', 'updated_at']:
            setattr(provider, key, value)
    storage.save()
    return jsonify(provider.to_dict())

@api_bp.route('/providers/<provider_id>', methods=['DELETE'], strict_slashes=False)
def delete_provider(provider_id):
    """ Delete a provider """
    provider = storage.get(Provider, provider_id)
    if not provider:
        abort(404)
    storage.delete(provider)
    storage.save()
    return jsonify({}), 200

# how do we track registered or served by a certain provider?
#@api_bp.route('/providers/<provider_id>/patients', methods=['GET'], strict_slashes=False)
#def get_provider_patients(provider_id):
#    """ Get all patients for a provider """
#    provider = storage.get(Provider, provider_id)
#    if not provider:
#        abort(404)
#    patients = provider.patients
#    return jsonify([patient.to_dict() for patient in patients])