from flask import Blueprint

api_bp = Blueprint("api_bp", __name__, url_prefix="/api/v1")

from api.v1.views.index import *
from api.v1.views.patient import *
from api.v1.views.error_handlers import *
from api.v1.views.user import *
from api.v1.views.role import *
from api.v1.views.auth import *
