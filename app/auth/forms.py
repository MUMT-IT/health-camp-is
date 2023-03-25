from flask_wtf import FlaskForm
from wtforms.validators import Email, EqualTo, InputRequired
from wtforms import EmailField, PasswordField, BooleanField
from wtforms_alchemy import model_form_factory, QuerySelectField, QuerySelectMultipleField

from app.services.models import *

BaseModelForm = model_form_factory(FlaskForm)


class ModelForm(BaseModelForm):
    @classmethod
    def get_session(self):
        return db.session


class UserForm(ModelForm):
    class Meta:
        model = User
        excludes = ['_password_hash', 'is_approved', 'has_admin_role', 'updated_at', 'registered_at', 'password']
    new_password = PasswordField('Password')
    confirm_password = PasswordField('Confirm Password',
                                     validators=[EqualTo('new_password', message='Password must match.')])


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[Email(), InputRequired()])
    password = PasswordField('Password')
    remember_me = BooleanField('Remember me')