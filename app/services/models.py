import datetime
import decimal

from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.validators import Email
from dateutil import relativedelta
from wtforms import widgets, RadioField
from flask_login import UserMixin

from app import db


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    email = db.Column('email', db.String(), info={'validators': Email(), 'label': 'Email'}, unique=True)
    title = db.Column('title', db.String(), info={'label': 'Title'})
    firstname = db.Column('firstname', db.String(), nullable=False, info={'label': 'First Name'})
    lastname = db.Column('lastname', db.String(), nullable=False, info={'label': 'Last Name'})
    has_admin_role = db.Column('has_admin_role', db.Boolean(), default=False)
    registered_at = db.Column('registered_at', db.DateTime(), server_default=func.now())
    updated_at = db.Column('updated_at', db.DateTime(),
                           server_default=func.now(), onupdate=func.now())
    is_approved = db.Column('is_approved', db.Boolean(), default=False)
    _password_hash = db.Column('password_hash', db.Text())

    @property
    def is_active(self):
        return self.is_approved

    @property
    def password(self):
        return ValueError

    def set_password(self, pwd):
        self._password_hash = generate_password_hash(pwd)

    def check_password(self, pwd):
        if check_password_hash(self._password_hash, pwd):
            return True
        else:
            False


underlying_diseases_health_records = db.Table(
    'underlying_diseases_health_records',
    db.Column('disease_id', db.ForeignKey('underlying_diseases.id'), primary_key=True),
    db.Column('health_record_id', db.ForeignKey('health_records.id'), primary_key=True)
)

family_diseases_health_records = db.Table(
    'family_diseases_health_records',
    db.Column('family_history_record_id', db.ForeignKey('family_diseases.id'), primary_key=True),
    db.Column('health_record_id', db.ForeignKey('health_records.id'), primary_key=True)
)


class Client(db.Model):
    __tablename__ = 'clients'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    firstname = db.Column('firstname', db.String(), nullable=False)
    lastname = db.Column('lastname', db.String(), nullable=False)
    pid = db.Column('pid', db.String(13), unique=True)
    dob = db.Column('dob', db.Date())
    client_number = db.Column('client_number', db.String(), unique=True)
    gender = db.Column('gender', db.String(), info={'label': 'เพศ',
                                                    'choices': [(c, c) for c in ['ชาย', 'หญิง']],
                                                    'form_field_class': RadioField})
    updated_at = db.Column('updated_at', db.DateTime(),
                           server_default=func.now(), onupdate=func.now())

    @property
    def age(self):
        if self.dob:
            return '{} ปี {} เดือน'.format(relativedelta.relativedelta(datetime.datetime.today(), self.dob).years,
                               relativedelta.relativedelta(datetime.datetime.today(), self.dob).months)
        else:
            return None

    @property
    def fullname(self):
        return f'{self.firstname} {self.lastname}'


class ClientPhysicalProfile(db.Model):
    __tablename__ = 'client_physical_profiles'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    client_id = db.Column('client_id', db.ForeignKey('clients.id'))
    client = db.relationship(Client, backref=db.backref('physical_profiles', cascade='all, delete-orphan'))
    weight = db.Column('weight', db.Numeric(), info={'label': 'น้ำหนักหน่วยกก.'})
    height = db.Column('height', db.Numeric(), info={'label': 'ส่วนสูงหน่วยซม.'})
    systolic = db.Column('systolic', db.Integer(), info={'label': 'Systolic'})
    diastolic = db.Column('diastolic', db.Integer(), info={'label': 'Diastolic'})
    updated_at = db.Column('updated_at', db.DateTime(),
                           server_default=func.now(), onupdate=func.now())
    waist = db.Column('waist', db.Numeric(), info={'label': 'รอบเอว'})

    @property
    def bmi(self):
        if self.weight and self.height:
            bmi = (self.weight) / (self.height * decimal.Decimal(.01)) ** 2
            return round(bmi, 2)
        else:
            return None

    def get_bmi_interpretation(self):
        if self.bmi:
            if self.bmi < 18.5:
                return 'ผอมกว่าเกณฑ์ปกติ'
            elif self.bmi < 25:
                return 'ปกติ'
            elif self.bmi < 30:
                return 'น้ำหนักเกินเกณฑ์ปกติ'
            else:
                return 'มีภาวะอ้วน'
        return '-'


class Test(db.Model):
    __tablename__ = 'tests'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    name = db.Column('name', db.String(), nullable=False)
    unit = db.Column('unit', db.String())
    reference = db.Column('reference', db.Text())
    min_value = db.Column('min_value', db.Numeric(), default=0)
    max_value = db.Column('max_value', db.Numeric(), default=1)
    updated_at = db.Column('updated_at', db.DateTime(),
                           server_default=func.now(), onupdate=func.now())
    min_interpret = db.Column('min_interpret', db.Text())
    max_interpret = db.Column('max_interpret', db.Text())


class TestRecord(db.Model):
    __tablename__ = 'test_records'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    client_id = db.Column('client_id', db.ForeignKey('clients.id'))
    client = db.relationship(Client, backref=db.backref('test_records',
                                                        lazy='dynamic',
                                                        cascade='all, delete-orphan'))
    test_id = db.Column('test_id', db.ForeignKey('tests.id'))
    test = db.relationship(Test, backref=db.backref('records', cascade='all, delete-orphan'))
    value = db.Column('value', db.String())
    updated_at = db.Column('updated_at', db.DateTime(),
                           server_default=func.now(), onupdate=func.now())
    note = db.Column('note', db.Text())

    @property
    def interpret(self):
        if float(self.value) > self.test.max_value:
            return 'High'
        elif float(self.value) < self.test.min_value:
            return 'Low'
        else:
            return 'Normal'


class Organism(db.Model):
    __tablename__ = 'organisms'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    name = db.Column('name', db.String(), nullable=False)

    def __str__(self):
        return self.name


class Stage(db.Model):
    __tablename__ = 'stages'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    stage = db.Column('stage', db.String(), nullable=False)

    def __str__(self):
        return self.stage


class UnderlyingDisease(db.Model):
    __tablename__ = 'underlying_diseases'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    name = db.Column('name', db.String(), nullable=False)

    def __str__(self):
        return self.name


class FamilyDiseases(db.Model):
    __tablename__ = 'family_diseases'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    name = db.Column('name', db.String(), nullable=False, info={'label': 'รายการ'})

    def __str__(self):
        return self.name


class HealthRecord(db.Model):
    __tablename__ = 'health_records'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    underlying_diseases = db.relationship(UnderlyingDisease,
                               secondary=underlying_diseases_health_records,
                               info={'label': 'โรคประจำตัว'})
    other_underlying_disease = db.Column('other_underlying_disease', db.String(), info={'label': 'โรคอื่น ๆ'})
    family_diseases = db.relationship(FamilyDiseases,
                                      secondary=family_diseases_health_records,
                                      info={'label': 'โรคประจำตัวในครอบครัว'})
    other_family_disease = db.Column('other_family_disease', db.String(), info={'label': 'โรคในครอบครัวอื่น ๆ'})
    fasting_datetime = db.Column('fasting_datetime', db.DateTime(), info={'label': 'อดอาหารเมื่อ'})
    client_id = db.Column('client_id', db.ForeignKey('clients.id'))
    client = db.relationship(Client, backref=db.backref('health_records',
                                                        cascade='all, delete-orphan', lazy='dynamic'))
    updated_at = db.Column('updated_at', db.DateTime(),
                           server_default=func.now(), onupdate=func.now())
    suggestion = db.Column('suggestion', db.Text(), info={'label': 'คำแนะนำ'})


class StoolTestRecord(db.Model):
    __tablename__ = 'stool_test_records'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    lab_number = db.Column('lab_number', db.String(), nullable=False, unique=True)
    client_id = db.Column('client_id', db.ForeignKey('clients.id'))
    client = db.relationship(Client, backref=db.backref('stool_exam_records',
                                                        cascade='all, delete-orphan'))
    updated_at = db.Column('updated_at', db.DateTime(),
                           server_default=func.now(), onupdate=func.now())
    note = db.Column('note', db.Text())
    collection_datetime = db.Column('collection_datetime', db.DateTime(), info={'label': 'เก็บตัวอย่างเมื่อ'})
    color = db.Column('color', db.String(), info={"label": 'Color',
                                                  'choices': [(c, c) for c in ['เหลือง', 'น้ำตาล', 'เขียว', 'ดำ', 'แดง', 'เทา']]})
    form = db.Column('form', db.String(), info={'label': 'Form',
                                                'choices': [(c, c) for c in ['แข็ง', 'นุ่ม', 'เหลวเป็นน้ำ', 'มีมูกเลือดปน']]})
    occult_blood = db.Column('occult_blood',
                             db.String(), info={'label': 'Occult blood',
                                                'choices': [(c,c) for c in ['ไม่ได้ทดสอบ', 'บวก', 'ลบ']]})
    # TODO: add others
    reported_at = db.Column('reported_at', db.DateTime())

    @property
    def results(self):
        return ','.join([str(item) for item in self.items])


class StoolTestReportItem(db.Model):
    __tablename__ = 'stool_test_report_items'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    org_id = db.Column('org_id', db.ForeignKey('organisms.id'))
    stage_id = db.Column('stage_id', db.ForeignKey('stages.id'))
    organism = db.relationship(Organism)
    stage = db.relationship(Stage)
    record_id = db.Column('record_id', db.ForeignKey('stool_test_records.id'))
    record = db.relationship(StoolTestRecord,
                             backref=db.backref('items', cascade='all, delete-orphan'))

    def __str__(self):
        return f'{self.organism} {self.stage}'
