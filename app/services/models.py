from sqlalchemy import func

from app import db


class Client(db.Model):
    __tablename__ = 'clients'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    firstname = db.Column('firstname', db.String(), nullable=False)
    lastname = db.Column('lastname', db.String(), nullable=False)
    pid = db.Column('pid', db.String(13))
    dob = db.Column('dob', db.Date())
    client_number = db.Column('client_number', db.String())

    @property
    def fullname(self):
        return f'{self.firstname} {self.lastname}'


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
    client = db.relationship(Client, backref=db.backref('clients', cascade='all, delete-orphan'))
    test_id = db.Column('test_id', db.ForeignKey('tests.id'))
    test = db.relationship(Test, backref=db.backref('records', cascade='all, delete-orphan'))
    value = db.Column('value', db.String())
    updated_at = db.Column('updated_at', db.DateTime(),
                           server_default=func.now(), onupdate=func.now())
    note = db.Column('note', db.Text())

