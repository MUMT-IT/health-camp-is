from flask import Blueprint

service_bp = Blueprint('services', __name__, url_prefix='/services')


from . import views