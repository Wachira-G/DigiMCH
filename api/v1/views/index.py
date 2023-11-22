
from api.v1.views import api_bp
from flask import jsonify


@api_bp.route('/status', methods=['GET'], strict_slashes=False)
def status():
    """ Status of API """
    return jsonify({"status": "OK"})