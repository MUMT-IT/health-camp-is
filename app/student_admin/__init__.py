from flask import Blueprint

admin_bp = Blueprint('student_admin', __name__, url_prefix='/student-student_admin')


from . import views