from flask_sqlalchemy import SQLAlchemy
import enum

db = SQLAlchemy()


class Year(enum.Enum):
    FRESHMAN = "Freshman"
    SOPHOMORE = "Sophomore"
    JUNIOR = "Junior"
    SENIOR = "Senior"


class Gender(enum.Enum):
    MALE = "Male"
    FEMALE = "Female"


organizations = db.Table('organizations',
                db.Column('organization_id', db.Integer, db.ForeignKey('organization.id'), primary_key=True),
                db.Column('student_id', db.Integer, db.ForeignKey('student.id'), primary_key=True)
)


class User(db.Model):
    __abstract__ = True
    username = db.Column(db.String(24), nullable=False)
    pw_hash = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(320))
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)


class Student(User):
    id = db.Column(db.Integer, primary_key=True)
    organizations = db.relationship('Organization', secondary=organizations, backref=db.backref('students'))

    # profile base attributes
    year = db.Column(db.Enum(Year), nullable=False)
    major = db.Column(db.String(50))
    minor = db.Column(db.String(50))
    resume = db.Column(db.LargeBinary)
    gender = db.Column(db.Enum(Gender))
    gpa = db.Column(db.Float)
    phone = db.Column(db.String(10))


class Organization(User):
    id = db.Column(db.Integer, primary_key=True)
    companies = db.relationship('Company', backref='organization', lazy=True)


class Company(User):
    id = db.Column(db.Integer, primary_key=True)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)