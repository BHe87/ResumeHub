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
    OTHER = "Other"


class WorkStatus(enum.Enum):
    VISA = "Require Visa sponsorship"
    USCITIZEN = "U.S. Citizen"


class Clearance(enum.Enum):
    PUBLICTRUST = "Public Trust"
    SECRET = "Secret"
    TOPSECRET = "Top Secret"
    CONFIDENTIAL = "Confidential"
    OTHER = "Other"
    NONE = "None of the above"


class SearchStatus(enum.Enum):
    ACTIVE = "Actively searching for opportunities"
    OPEN = "Not actively searching, but open to opportunities"
    CLOSED = "Not open to opportunities"


organizations_and_students = db.Table('organizations_and_students',
                db.Column('organization_id', db.Integer, db.ForeignKey('organization.id'), primary_key=True),
                db.Column('student_id', db.Integer, db.ForeignKey('student.id'), primary_key=True),
                db.UniqueConstraint('organization_id', 'student_id', name='student_organization_no_duplicate'))

organizations_and_companies = db.Table('organizations_and_companies',
                db.Column('organization_id', db.Integer, db.ForeignKey('organization.id'), primary_key=True),
                db.Column('company_id', db.Integer, db.ForeignKey('company.id'), primary_key=True),
                db.UniqueConstraint('organization_id', 'company_id', name='company_organization_no_duplicate'))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(24), nullable=False)
    pw_hash = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(320))
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)


class Student(User):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    organizations = db.relationship('Organization', secondary=organizations_and_students, backref=db.backref('students'))

    # profile base attributes
    year = db.Column(db.Enum(Year), nullable=False)
    major = db.Column(db.String(50))
    minor = db.Column(db.String(50))
    gender = db.Column(db.Enum(Gender))
    gpa = db.Column(db.Float)
    phone = db.Column(db.String(10))

    # Resume file
    resume = db.Column(db.LargeBinary)
    filename = db.Column(db.String(50))


class Organization(User):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)

    # TODO: set up correct relationship between Organization and Company
    # company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    # companies = db.relationship('Company', foreign_keys=[company_id])


class Company(User):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    # sponsor_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)