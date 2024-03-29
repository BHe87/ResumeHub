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
                # I do not think this UniqueConstraint works.. I (Jamie) will keep my TODO in /add_organization
                db.UniqueConstraint('organization_id', 'student_id', name='student_organization_no_duplicate'))

organizations_and_companies = db.Table('organizations_and_companies',
                db.Column('organization_id', db.Integer, db.ForeignKey('organization.id'), primary_key=True),
                db.Column('company_id', db.Integer, db.ForeignKey('company.id'), primary_key=True),
                db.UniqueConstraint('organization_id', 'company_id', name='company_organization_no_duplicate'))

pending_orgs_and_students = db.Table('pending_orgs_and_students',
                db.Column('student_id', db.Integer, db.ForeignKey('student.id'), primary_key=True),
                db.Column('organization_id', db.Integer, db.ForeignKey('organization.id'), primary_key=True),
                db.UniqueConstraint('organization_id', 'student_id', name='pending_student_organization_no_duplicate'))

pending_orgs_and_companies = db.Table('pending_orgs_and_companies',
                db.Column('company_id', db.Integer, db.ForeignKey('company.id'), primary_key=True),
                db.Column('organization_id', db.Integer, db.ForeignKey('organization.id'), primary_key=True),
                db.UniqueConstraint('organization_id', 'company_id', name='pending_company_organization_no_duplicate'))



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(24), nullable=False)
    pw_hash = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(320), nullable=False)
    #first_name = db.Column(db.String(50), nullable=False)
    #last_name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)


# Admin role model
class Admin(User):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)


class Student(User):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    pending_organizations = db.relationship('Organization', secondary=pending_orgs_and_students, lazy='subquery', backref=db.backref('pending_students', lazy=True))
    organizations = db.relationship('Organization', secondary=organizations_and_students, backref=db.backref('students'))

    # profile base attributes
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Enum(Year), nullable=False)
    major = db.Column(db.String(50), nullable=False)
    minor = db.Column(db.String(50))
    skills = db.Column(db.Text)
    gender = db.Column(db.Enum(Gender), nullable=False)
    gpa = db.Column(db.Float)
    work_status = db.Column(db.Enum(WorkStatus))
    clearance = db.Column(db.Enum(Clearance))
    search_status = db.Column(db.Enum(SearchStatus))
    phone = db.Column(db.String(10))

    # Resume file
    resume = db.Column(db.LargeBinary)
    filename = db.Column(db.String(50))


class Organization(User):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    # Andrea: I set up this relationship, not sure if I did the backref correctly
    companies = db.relationship('Company', secondary=organizations_and_companies, backref=db.backref('organizations'))
    # TODO: set up correct relationship between Organization and Company
    # company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    # companies = db.relationship('Company', foreign_keys=[company_id])

    name = db.Column(db.String(100), nullable=False)
    # Andrea: how to set up list of Students affiliated? Is this done here or just queried when needed?
    # Jamie: No need to do ^^ this, Organization.students will query a list of students affiliated


class Company(User):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    # sponsor_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)

    name = db.Column(db.String(100), nullable=False)
    # Andrea: need access code here or no?
    # Andrea: do we have an attribute for the Org that gave permission, or is it just queried?
    # Jamie: No need to do this neither. Company.organization will be queried as a list of organization affiliated

    pending_organizations = db.relationship('Organization', secondary=pending_orgs_and_companies, lazy='subquery', backref=db.backref('pending_companies', lazy=True))
