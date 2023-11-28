""" Error handlers for API v1."""

from api.v1.views import api_bp
from flask import jsonify


def register_error_handlers(app):
    """Register error handlers."""
    app.register_error_handler(400, bad_request)
    app.register_error_handler(404, not_found)
    app.register_error_handler(401, unauthorized)
    app.register_error_handler(403, forbidden)
    app.register_error_handler(405, method_not_allowed)
    app.register_error_handler(409, conflict)
    app.register_error_handler(429, too_many_requests)
    app.register_error_handler(500, internal_server_error)
    app.register_error_handler(503, service_unavailable)
    app.register_error_handler(504, gateway_timeout)
    app.register_error_handler(501, not_implemented)


# ----- client side errors -----#

# add error handler for 400
@api_bp.errorhandler(400)
def bad_request(error):
    """ Error handler for 400 """
    return jsonify({"error": error.description}), 400


# add error handler for 404
@api_bp.errorhandler(404)
def not_found(error):
    """ Error handler for 404 """
    return jsonify({"error": "Not found"}), 404


# add error handler for 401
@api_bp.errorhandler(401)
def unauthorized(error):
    """ Error handler for 401 """
    return jsonify({"error": error.description}), 401


# add error handler for 403
@api_bp.errorhandler(403)
def forbidden(error):
    """ Error handler for 403 """
    return jsonify({"error": error.description}), 403


# add error handler for 405
@api_bp.errorhandler(405)
def method_not_allowed(error):
    """ Error handler for 405 """
    return jsonify({"error": error.description}), 405


# add error handler for 409
@api_bp.errorhandler(409)
def conflict(error):
    """ Error handler for 409 """
    return jsonify({"error": error.description}), 409


# add error handler for 429
@api_bp.errorhandler(429)
def too_many_requests(error):
    """ Error handler for 429 """
    return jsonify({"error": error.description}), 429


# ----- server side errors -----#

# add error handler for 500
@api_bp.errorhandler(500)
def internal_server_error(error):
    """ Error handler for 500 """
    return jsonify({"error": "Internal server error"}), 500


# add error handler for 503
@api_bp.errorhandler(503)
def service_unavailable(error):
    """ Error handler for 503 """
    return jsonify({"error": error.description}), 503


# add error handler for 504
@api_bp.errorhandler(504)
def gateway_timeout(error):
    """ Error handler for 504 """
    return jsonify({"error": error.description}), 504


# add error handler for 501
@api_bp.errorhandler(501)
def not_implemented(error):
    """ Error handler for 501 """
    return jsonify({"error": error.description}), 501
