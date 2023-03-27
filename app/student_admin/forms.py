from flask_wtf import FlaskForm
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
