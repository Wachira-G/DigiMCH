from flask import Blueprint

api_bp = Blueprint("api_bp", __name__, url_prefix="/api/v1")

from api.v1.views.index import *
from api.v1.views.location import *
from api.v1.views.patient import *
from api.v1.views.error_handlers import *
from api.v1.views.user import *
from api.v1.views.role import *
from api.v1.views.appointment import *
from api.v1.views.visit import *
from api.v1.views.encounter import *
from api.v1.views.pregnancy_history import *
from api.v1.views.medical_history import *
from api.v1.views.first_visit_examination import *
from api.v1.views.present_pregnancy import *
from api.v1.views.antenatal_profile import *
from api.v1.views.maternal_profile import *
from api.v1.views.clinical_note import *
