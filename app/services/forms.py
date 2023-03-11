from flask_wtf import FlaskForm
from wtforms import FormField, FieldList
from wtforms_alchemy import model_form_factory, QuerySelectField

from app import db
from app.services.models import *

BaseModelForm = model_form_factory(FlaskForm)


class ModelForm(BaseModelForm):
    @classmethod
    def get_session(self):
        return db.session


class ClientForm(ModelForm):
    class Meta:
        model = Client


class ClientPhysicalProfileForm(ModelForm):
    class Meta:
        model = ClientPhysicalProfile


class TestForm(ModelForm):
    class Meta:
        model = Test


class TestRecordForm(ModelForm):
    class Meta:
        model = TestRecord


class StoolTestReportItemForm(ModelForm):
    class Meta:
        model = StoolTestReportItem
    organism = QuerySelectField('Organism', query_factory=lambda: Organism.query.all(),
                                get_label='name')
    stage = QuerySelectField('Stage', query_factory=lambda: Stage.query.all(),
                             get_label='stage')


class StoolTestForm(ModelForm):
    class Meta:
        model = StoolTestRecord

    items = FieldList(FormField(StoolTestReportItemForm,
                                default=StoolTestReportItem), min_entries=1)