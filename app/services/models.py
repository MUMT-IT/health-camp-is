from app import db


class Client(db.Model):
    __tablename__ = 'clients'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    firstname = db.Column('firstname', db.String(), nullable=False)
    lastname = db.Column('lastname', db.String(), nullable=False)
    pid = db.Column('pid', db.String(13))
    dob = db.Column('dob', db.Date())
    client_number = db.Column('client_number', db.String())
