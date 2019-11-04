from flask_sqlalchemy import SQLAlchemy
import enum

db = SQLAlchemy()


class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(24), nullable=False)
	pw_hash = db.Column(db.String(64), nullable=False)


class Year(enum.Enum):
    FRESHMAN = "Freshman"
    SOPHOMORE = "Sophomore"
    JUNIOR = "Junior"
    SENIOR = "Senior"


class Gender(enum.Enum):
    MALE = "Male"
    FEMALE = "Female"


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(24), nullable=False)
    pw_hash = db.Column(db.String(64), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)

    # profile base attributes
    year = db.Column(db.Enum(Year), nullable=False)
    major = db.Column(db.String(50))
    minor = db.Column(db.String(50))
    resume = db.Column(db.LargeBinary)
    gender = db.Column(db.Enum(Gender))
    gpa = db.Column(db.Float)
    phone = db.Column(db.String(10))


class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(24), nullable=False)
    pw_hash = db.Column(db.String(64), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    companies = db.relationship('Company', backref='organization', lazy=True)


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(24), nullable=False)
    pw_hash = db.Column(db.String(64), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)