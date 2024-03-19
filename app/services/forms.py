from flask_wtf import FlaskForm
from wtforms import FormField, FieldList, BooleanField
from wtforms_alchemy import model_form_factory, QuerySelectField, QuerySelectMultipleField

from app import db
from app.services.models import *

BaseModelForm = model_form_factory(FlaskForm)


class ModelForm(BaseModelForm):
    @classmethod
    def get_session(self):
        return db.session


def create_client_form(project_id):
    class ClientForm(ModelForm):
        class Meta:
            model = Client

        address = QuerySelectField('ที่อยู่',
                                   query_factory=lambda: ClientAddress.query.filter_by(project_id=project_id),
                                   get_label='name')
        use_pid_as_hn = BooleanField('ใช้หมายเลขบัตรปชช.เป็นรหัสผู้รับบริการ', default=False)

    return ClientForm


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

    not_found = RadioField('Not found', choices=[(c, c) for c in ['Found', 'Not found']], default='Not found')

    items = FieldList(FormField(StoolTestReportItemForm,
                                default=StoolTestReportItem), min_entries=1)


class HealthRecordForm(ModelForm):
    class Meta:
        model = HealthRecord

    underlying_diseases = QuerySelectMultipleField('โรคประจำตัว',
                                                   query_factory=lambda: UnderlyingDisease.query.all(),
                                                   get_label='name',
                                                   allow_blank=True,
                                                   blank_text='กรุณาระบุโรค',
                                                   widget=widgets.ListWidget(prefix_label=False),
                                                   option_widget=widgets.CheckboxInput())
    family_diseases = QuerySelectMultipleField('โรคประจำตัวในครอบครัว',
                                               query_factory=lambda: FamilyDiseases.query.all(),
                                               get_label='name',
                                               allow_blank=True,
                                               blank_text='กรุณาระบุโรค',
                                               widget=widgets.ListWidget(prefix_label=False),
                                               option_widget=widgets.CheckboxInput())
