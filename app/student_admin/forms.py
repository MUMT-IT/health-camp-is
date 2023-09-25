from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import BooleanField
from wtforms_alchemy import model_form_factory

from app import db
from app.services.models import *

BaseModelForm = model_form_factory(FlaskForm)


class ModelForm(BaseModelForm):
    @classmethod
    def get_session(self):
        return db.session


class AddressForm(ModelForm):
    class Meta:
        model = ClientAddress


class OrganismForm(ModelForm):
    class Meta:
        model = Organism


class ClientUploadForm(FlaskForm):
    upload = FileField('File Upload', validators=[FileRequired()])
    random_pid = BooleanField('Generate random PID', default=False)
    use_lab_number_as_client_number = BooleanField('Use lab number as client number', default=False)
