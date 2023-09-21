import datetime
import decimal

from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.validators import Email
from dateutil import relativedelta
from wtforms import widgets, RadioField
from flask_login import UserMixin

from app import db


class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    name = db.Column('name', db.String(), info={'label': 'ชื่อโครงการ'})


class ClientAddress(db.Model):
    __tablename__ = 'client_addresses'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    name = db.Column('name', db.String(), info={'label': 'ที่อยู่'})
    project_id = db.Column(db.ForeignKey('projects.id'))
    project = db.relationship(Project, backref=db.backref('client_addresses'))

    def __str__(self):
        return self.name


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    email = db.Column('email', db.String(), info={'validators': Email(), 'label': 'Email'}, unique=True)
    title = db.Column('title', db.String(), info={'label': 'Title'})
    firstname = db.Column('firstname', db.String(), nullable=False, info={'label': 'First Name'})
    lastname = db.Column('lastname', db.String(), nullable=False, info={'label': 'Last Name'})
    license_id = db.Column('license_id', db.String(), nullable=True,
                           info={'label': 'ท.น.'})
    has_admin_role = db.Column('has_admin_role', db.Boolean(), default=False)
    registered_at = db.Column('registered_at', db.DateTime(), server_default=func.now())
    updated_at = db.Column('updated_at', db.DateTime(),
                           server_default=func.now(), onupdate=func.now())
    is_approved = db.Column('is_approved', db.Boolean(), default=False)
    _password_hash = db.Column('password_hash', db.Text())

    @property
    def fullname(self):
        return f'{self.title}{self.firstname} {self.lastname}'

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
    firstname = db.Column('firstname', db.String(), nullable=False, info={'label': 'ชื่อ'})
    lastname = db.Column('lastname', db.String(), nullable=False, info={'label': 'นามสกุล'})
    pid = db.Column('pid', db.String(13), unique=True, info={'label': 'หมายเลขบัตรประชาชน'})
    dob = db.Column('dob', db.Date(), info={'label': 'วันเดือนปีเกิด'})
    age_ = db.Column('age', db.Integer, info={'label': 'อายุ'})
    client_number = db.Column('client_number', db.String(), unique=True, info={'label': 'รหัสผู้รับบริการ'})
    gender = db.Column('gender', db.String(), info={'label': 'เพศ',
                                                    'choices': [(c, c) for c in ['ชาย', 'หญิง']],
                                                    'form_field_class': RadioField})
    updated_at = db.Column('updated_at', db.DateTime(),
                           server_default=func.now(), onupdate=func.now())
    address_id = db.Column('address_id', db.ForeignKey('client_addresses.id'))
    address = db.relationship(ClientAddress, backref=db.backref('clients'))
    updated_id = db.Column('updater_id', db.ForeignKey('users.id'))
    updated_by = db.relationship(User)
    project_id = db.Column(db.ForeignKey('projects.id'))
    project = db.relationship(Project, backref=db.backref('clients'))

    @property
    def age(self):
        if self.age_:
            return f'{self.age_} ปี'
        else:
            return '{} ปี {} เดือน'.format(relativedelta.relativedelta(datetime.datetime.today(), self.dob).years,
                                           relativedelta.relativedelta(datetime.datetime.today(), self.dob).months)

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
    updater_id = db.Column('updater_id', db.ForeignKey('users.id'))
    updated_by = db.relationship(User)
    waist = db.Column('waist', db.Numeric(), info={'label': 'รอบเอว'})

    @property
    def bp(self):
        return f'{self.systolic}/{self.diastolic} mmHg'

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
                return 'ผอมเกินไป'
            elif self.bmi < 25:
                return 'ปกติ'
            elif self.bmi < 30:
                return 'นน.เกิน'
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
    updater_id = db.Column('updater_id', db.ForeignKey('users.id'))
    updated_by = db.relationship(User)
    note = db.Column('note', db.Text())

    @property
    def interpret(self):
        if float(self.value) > self.test.max_value:
            return 'สูง'
        elif float(self.value) < self.test.min_value:
            return 'ต่ำ'
        else:
            return 'ปกติ'


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
    fasting_time = db.Column('fasting_time', db.Numeric(), info={'label': 'อดอาหารมาแล้ว (ชม.)'})
    client_id = db.Column('client_id', db.ForeignKey('clients.id'))
    client = db.relationship(Client, backref=db.backref('health_records',
                                                        cascade='all, delete-orphan', lazy='dynamic'))
    updated_at = db.Column('updated_at', db.DateTime(),
                           server_default=func.now(), onupdate=func.now())
    suggestion = db.Column('suggestion', db.Text(), info={'label': 'คำแนะนำ'})
    updater_id = db.Column('updater_id', db.ForeignKey('users.id'))
    updated_by = db.relationship(User)


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
                                                  'choices': [(c, c) for c in
                                                              ['เหลือง', 'น้ำตาล', 'เขียว', 'ดำ', 'แดง', 'เทา',
                                                               'ไม่ได้ส่งอุจจาระ']]})
    form = db.Column('form', db.String(), info={'label': 'Form',
                                                'choices': [(c, c) for c in
                                                            ['แข็ง', 'นุ่ม', 'เหลวเป็นน้ำ', 'มีมูกเลือดปน',
                                                             'ไม่ได้ส่งอุจจาระ']]})
    occult_blood = db.Column('occult_blood',
                             db.String(), info={'label': 'Occult blood',
                                                'choices': [(c, c) for c in ['ไม่ได้ทดสอบ', 'บวก', 'ลบ']]})
    method = db.Column('method', db.String(),
                       info={'label': 'วิธีการตรวจ',
                             'choices': [(c, c) for c in ['Direct smear', 'Scotch tape technique']],
                             'form_field_class': RadioField
                             })
    quality = db.Column('quality', db.String(),
                        info={'label': 'คุณภาพสิ่งตัวอย่าง',
                              'choices': [(c, c) for c in ['ไม่เหมาะสม', 'พอใช้', 'เหมาะสม']],
                              'form_field_class': RadioField,
                              })
    reported_at = db.Column('reported_at', db.DateTime(timezone=True))
    reporter_id = db.Column('reporter_id', db.ForeignKey('users.id'))
    updater_id = db.Column('updater_id', db.ForeignKey('users.id'))
    approved_at = db.Column('approved_at', db.DateTime(timezone=True))
    approver_id = db.Column('approver_id', db.ForeignKey('users.id'))
    reported_by = db.relationship(User, foreign_keys=[reporter_id])
    updated_by = db.relationship(User, foreign_keys=[updater_id])
    approved_by = db.relationship(User, foreign_keys=[approver_id])

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
        if self.organism.name == 'Not found':
            return f'Not found'
        else:
            return f'{self.organism} {self.stage}'
