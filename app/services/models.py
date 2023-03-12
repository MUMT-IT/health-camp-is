from sqlalchemy import func
from wtforms import widgets, RadioField

from app import db


class Client(db.Model):
    __tablename__ = 'clients'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    firstname = db.Column('firstname', db.String(), nullable=False)
    lastname = db.Column('lastname', db.String(), nullable=False)
    pid = db.Column('pid', db.String(13))
    dob = db.Column('dob', db.Date())
    client_number = db.Column('client_number', db.String())
    gender = db.Column('gender', db.String(), info={'label': 'เพศ',
                                                    'choices': [(c, c) for c in ['ชาย', 'หญิง']],
                                                    'form_field_class': RadioField})

    @property
    def fullname(self):
        return f'{self.firstname} {self.lastname}'

    # TODO: age calculation


class ClientPhysicalProfile(db.Model):
    __tablename__ = 'client_physical_profiles'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    client_id = db.Column('client_id', db.ForeignKey('clients.id'))
    client = db.relationship(Client, backref=db.backref('physical_profiles',
                                                        lazy='dynamic',
                                                        cascade='all, delete-orphan'))
    weight = db.Column('weight', db.Numeric(), info={'label': 'น้ำหนักหน่วยกก.'})
    height = db.Column('height', db.Numeric(), info={'label': 'ส่วนสูงหน่วยซม.'})
    systolic = db.Column('systolic', db.Integer(), info={'label': 'Systolic'})
    diastolic = db.Column('diastolic', db.Integer(), info={'label': 'Diastolic'})
    updated_at = db.Column('updated_at', db.DateTime(),
                           server_default=func.now(), onupdate=func.now())


class Test(db.Model):
    __tablename__ = 'tests'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    name = db.Column('name', db.String(), nullable=False)
    unit = db.Column('unit', db.String())
    reference = db.Column('reference', db.Text())
    updated_at = db.Column('updated_at', db.DateTime(),
                           server_default=func.now(), onupdate=func.now())


class TestRecord(db.Model):
    __tablename__ = 'test_records'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    client_id = db.Column('client_id', db.ForeignKey('clients.id'))
    client = db.relationship(Client, backref=db.backref('test_records',
                                                        cascade='all, delete-orphan'))
    test_id = db.Column('test_id', db.ForeignKey('tests.id'))
    test = db.relationship(Test, backref=db.backref('records', cascade='all, delete-orphan'))
    value = db.Column('value', db.String())
    updated_at = db.Column('updated_at', db.DateTime(),
                           server_default=func.now(), onupdate=func.now())
    note = db.Column('note', db.Text())


class Organism(db.Model):
    __tablename__ = 'organisms'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    name = db.Column('name', db.String(), nullable=False)


class Stage(db.Model):
    __tablename__ = 'stages'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    stage = db.Column('stage', db.String(), nullable=False)


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
    color = db.Column('color', db.String(), info={"label": 'Color',
                                                  'choices': [(c, c) for c in ['เหลือง', 'น้ำตาล', 'เขียว', 'ดำ', 'แดง', 'เทา']]})
    form = db.Column('form', db.String(), info={'label': 'Form',
                                                'choices': [(c, c) for c in ['แข็ง', 'นุ่ม', 'เหลวเป็นน้ำ', 'มีมูกเลือดปน']]})
    occult_blood = db.Column('occult_blood',
                             db.String(), info={'label': 'Occult blood',
                                                'choices': [(c,c) for c in ['ไม่ได้ทดสอบ', 'บวก', 'ลบ']]})
    # TODO: add others
    reported_at = db.Column('reported_at', db.DateTime())


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
