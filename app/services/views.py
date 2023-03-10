from flask import render_template

from app.services import service_bp as services


@services.route('/')
def index():
    return 'Welcome to our services'