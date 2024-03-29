from flask import Flask, redirect, render_template, url_for, g, session, request, abort, flash, make_response, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug import check_password_hash, generate_password_hash, secure_filename

from model import Admin, Company, db, Gender, Organization, Student, User, Year, WorkStatus, Clearance, SearchStatus
from werkzeug.datastructures import FileStorage

import os, io
from base64 import b64encode

# init
app = Flask(__name__)

app.config.update(dict(
	SECRET_KEY='GROUP18_RESUMEHUB',
	USERNAME='admin',
	PASSWORD='greatpassword',
	SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.root_path, 'resumehub.db'),
	SQLALCHEMY_TRACK_MODIFICATIONS = False
))

db.init_app(app)


@app.cli.command('initdb')
def initdb_command():
	# Drop the database and create the new one
	db.drop_all()
	db.create_all()

	# Hardcode the admin account
	db.session.add(Admin(username='admin',
						 pw_hash=generate_password_hash('admin'),
						 email='admin@resumehub.com',
						 description='I am an admin ;)'))

	# Hardcode `Human` student
	db.session.add(Student(username='Human',
						   pw_hash=generate_password_hash('123456'),
						   email='test@resumehub.com',
						   description='I am a student',
						   first_name='Human',
						   last_name='Namuh',
						   year=Year.SENIOR,
						   major='CS',
						   minor='LIFE',
						   gender=Gender.OTHER,
						   gpa=4.0,
						   work_status=WorkStatus.USCITIZEN,
						   clearance=Clearance.NONE,
						   search_status=SearchStatus.OPEN,
						   phone='4128933928'))
	# Hardcode `Ariana` student
	db.session.add(Student(username='Ariana',
						   pw_hash=generate_password_hash('ariana'),
						   email='ariana@resumehub.com',
						   description='I am a student in CS',
						   first_name='ariana',
						   last_name='grande',
						   year=Year.JUNIOR,
						   major='CS',
						   minor='IS',
						   gender=Gender.OTHER,
						   gpa=3.88,
						   work_status=WorkStatus.USCITIZEN,
						   clearance=Clearance.NONE,
						   search_status=SearchStatus.OPEN,
						   phone='4129339992'))


	# hardcode organization(s)
	db.session.add(Organization(username='Fresa',
								pw_hash=generate_password_hash('fresa'),
								email='Fresa@pitt.edu',
								description='Dance together!',
								name='Fresa'))
	db.session.add(Organization(username='KSA',
								pw_hash=generate_password_hash('ksa'),
								email='KSA@pitt.edu',
								description='Koreans squads!',
								name='KSA'))
	db.session.add(Organization(username='ASA',
								pw_hash=generate_password_hash('asa'),
								email='ASA@pitt.edu',
								description='Asian squads!',
								name='ASA'))
	db.session.add(Organization(username='WiCS',
								pw_hash=generate_password_hash('wics'),
								email='WiCS@pitt.edu',
								description='Women in CS!',
								name='WiCS'))
	db.session.add(Organization(username='GlobalTie',
								pw_hash=generate_password_hash('globaltie'),
								email='GlobalTie@pitt.edu',
								description='Global Tie!',
								name='GlobalTie'))

	# Hardcode company(s)
	db.session.add(Company(username='Google',
						   pw_hash=generate_password_hash('google'),
						   email='g@google.com',
						   description='OH YESSSSS',
						   name='GOOGLE'))

	db.session.commit()
	print('Initialized the database')


@app.before_request
def before_request():
	g.user = None
	if 'user_id' in session and 'role' in session:
		role = session['role']
		if role == 'student':
			g.user = Student.query.get(session['user_id'])
		elif role == 'organization':
			g.user = Organization.query.get(session['user_id'])
		elif role == 'admin':
			g.user = Admin.query.get(session['user_id'])
		# A user is logged in as Company
		else:
			g.user = Company.query.get(session['user_id'])


@app.route('/')
def root():
	# if not logged in
	if not g.user:
		return redirect(url_for('login'))
	
	organizations = None
	students = None
	all_organizations = None
	companies = None
	if type(g.user) is Student:
		organizations = g.user.organizations
	# will display the own organization info; therefore, no need to assign `organizations`
	elif type(g.user) is Organization:
		print('TODO: Do whatever we need here')
	elif type(g.user) is Admin:
		students = Student.query.all()
		all_organizations = Organization.query.all()
		companies = Company.query.all()
	elif type(g.user) is Company:
		organizations = g.user.organizations
	else:
		print("Error - Who is this ?");
	return render_template('index.html',
							organizations=organizations,
							students=students,
							all_organizations=all_organizations,
							companies=companies) 
	

@app.route('/login', methods=['GET', 'POST'])
def login():
	# if already logged in
	if g.user:
		return redirect(url_for('root'))

	error = None
	if request.method == 'POST':
		user = User.query.filter_by(username=request.form['username']).first()
		if user is None:
			error = 'Invalid username'
		elif not check_password_hash(user.pw_hash, request.form['password']):
			error = 'Invalid password'
		else:
			# A hacky way to determine if a user is Student, Organization, or Company
			if Student.query.get(user.id):
				role = 'student'
			elif Organization.query.get(user.id):
				role = 'organization'
			elif Admin.query.get(user.id):
				role = 'admin'
			# A user is registered as Company
			else:
				role = 'company'
			# Store a type of user role (Student, Organization, or Company) as well as user.id
			session['user_id'] = user.id
			session['role'] = role
			return redirect(url_for('root'))
	return render_template('login.html', error=error)


@app.route('/logout')
def logout():
	# if already logged in
	if not g.user:
		return redirect(url_for('root'))

	flash('You were logged out!')
	session.pop('user_id', None)
	
	return redirect(url_for('login'))


# TODO: check username and email constraints
# elif User.query.filter_by(username=request.form['username']).first():
# 	error = request.form['username'] + ' - This username is in use'
# elif User.query.filter_by(email=request.form['email']).first():
# 	error = request.form['email'] + ' - This email is in use'
@app.route('/register', methods=['GET', 'POST'])
def register():
	# if already logged in
	if g.user:
		return redirect(url_for('index'))
	
	error = None
	if request.method == 'POST':
		user_type = request.form['accountType']

		if user_type == 'Student':
			#assert request.form['username'] == None, 'Please, enter a username'

			if not request.form['username']:
				error = 'Please, enter a username'
			elif not request.form['password']:
				error = 'Please, enter a password'
			elif not request.form['password2']:
				error = 'Please, enter a password'
			elif request.form['password'] != request.form['password2']:
				error = 'Passwords do not match!'
			elif not request.form['email']:
				error = 'Please, enter an email'
			elif not request.form['firstName']:
				error = 'Please, enter a first name'
			elif not request.form['lastName']:
				error = 'Please, enter a last name'
			elif not request.form['major']:
				error = 'Please, enter a major'
			elif not request.form['minor']:
				error = 'Please, enter a minor'
			elif not request.form['phoneNumber']:
				error = 'Please, enter a phone number'
			elif len(request.form['phoneNumber']) != 10:
				error = 'Please, enter a 10-digit valid phone number without dash'
			elif not request.form['GPA']:
				error = 'Please, enter a GPA'
			else:
				flash('Your student account was successfully registered!')
				db.session.add(Student(username=request.form['username'],
									pw_hash=generate_password_hash(request.form['password']),
									email=request.form['email'],
									first_name=request.form['firstName'],
									last_name=request.form['lastName'],
									year=request.form['grade'],
									major=request.form['major'],
									minor=request.form['minor'],
									gender=request.form['gender'],
									gpa=request.form['GPA'],
									phone=request.form['phoneNumber']))
				db.session.commit()
				return redirect(url_for('login'))

		elif user_type == 'Organization':
			if not request.form['username']:
				error = 'Please, enter a username'
			elif not request.form['password']:
				error = 'Please, enter a password'
			elif not request.form['password2']:
				error = 'Please, enter a password'
			elif request.form['password'] != request.form['password2']:
				error = 'Passwords do not match!'
			elif not request.form['email']:
				error = 'Please, enter an email'
			elif not request.form['orgname']:
				error = 'Please, enter an organization name'
			else:
				flash('Your student organization account was successfully registered!')
				db.session.add(Organization(username=request.form['username'],
									pw_hash=generate_password_hash(request.form['password']),
									email=request.form['email'],
									name=request.form['orgname']))
				db.session.commit()
				return redirect(url_for('login'))

		elif user_type == 'Company':
			if not request.form['username']:
				error = 'Please, enter a username'
			elif not request.form['password']:
				error = 'Please, enter a password'
			elif not request.form['password2']:
				error = 'Please, enter a password'
			elif request.form['password'] != request.form['password2']:
				error = 'Passwords do not match!'
			elif not request.form['email']:
				error = 'Please, enter an email'
			elif not request.form['companyname']:
				error = 'Please, enter a company name'
			else:
				flash('Your company account was successfully registered!')
				db.session.add(Company(username=request.form['username'],
									pw_hash=generate_password_hash(request.form['password']),
									email=request.form['email'],
									name=request.form['companyname']))
				db.session.commit()
				return redirect(url_for('login'))

	# if request.method == 'GET'
	return render_template('register.html',
							YEAR=Year,
							GENDER=Gender,
							error=error)


@app.route('/profile')
def profile():
	# Check if user is not logged in. SKIP FOR NOW
	if not g.user:
		return redirect(url_for('login'))

	resume = None
	if session['role'] == 'student' and g.user.resume is not None:
		resume = b64encode(g.user.resume)

	return render_template('profile.html',
						   current_student=g.user,
						   organizations=Organization.query.all(),
						   YEAR=Year,
						   GENDER=Gender,
						   resume=resume)


@app.route('/save_profile', methods=['POST'])
def save_profile():
	if not g.user:
		return redirect(url_for('login'))

	student = Student.query.get(session['user_id'])

	if student == None:
		print("Error: Student in NULL when saving profile", flush=True)

	# Collect which fields we are missing
	warn = ""
	isSaved = False

	# Check we have stuff for each field
	# Ideally we auto fill the info they already have?
	if request.method == 'POST':
		if not request.form['first-name']:
			warn += "Missing name\n"
		else:
		 	student.first_name = request.form.getlist('first-name')[0] # just use first name for now lol

		if not request.form['last-name']:
			warn += "Missing name\n"
		else:
		 	student.last_name = request.form.getlist('last-name')[0] # just use first name for now lol

		if not request.form['major']:
			warn += "Missing major\n"
		else:
			student.major = request.form.getlist('major')[0]

		if not request.form['minor']:
			warn += "Missing minor\n"
		else:
			student.minor = request.form.getlist('minor')[0]

		if not request.form['grade']:
			warn += "Missing grade\n"
		else:
			student.year = request.form.getlist('grade')[0]

		if not request.form['gender']:
			warn += "Missing gender\n" # TRIGGER WARNING
		else:
			student.gender = request.form.getlist('gender')[0]

		if not request.form['gpa']:
			warn += "Missing GPA\n"
		else:
			student.gpa = request.form.getlist('gpa')[0]

		if not request.form['phone']:
			warn += "Missing phone number\n"
		else:
			student.phone = request.form.getlist('phone')[0]

		print("Warning: {}\n".format(warn))

		# Save to database
		db.session.commit()

		# Set the url parameter to true, since it has been saved to database
		isSaved = True
	
	print("Ayy got it boss")
	return redirect(url_for('student_submission', result=isSaved))

@app.route('/student_submission')
def student_submission():
	if not g.user:
		return redirect(url_for('login'))

	# Get the url argument to see if the profile was successfully saved
	# The == Converts it into a boolean if the argument is "True"
	isSaved = request.args.get('result') == "True"

	return render_template('student_submission.html', result=isSaved)

	
@app.route('/add_organization', methods=['POST'])
def add_organization():
	if not g.user:
		return redirect(url_for('login'))	
	# save selected organization to the user (student)
	organization = Organization.query.filter_by(username=request.form['organization']).first()
	current_user = g.user
	# check if a student has already joined the organization;
	# TODO: Remove this, and add UniqueConstraint to `organizations` in model.py in order to handle this properly
	if organization in current_user.organizations:
		return redirect(url_for('profile'))

	current_user.pending_organizations.append(organization)
	db.session.commit()

	return render_template('student_submission.html', 
							result='true', 
							YEAR=Year)


@app.route('/save_resume', methods=['POST'])
def save_resume():
	if not g.user:
		return redirect(url_for('login'))	

	student = Student.query.get(session['user_id'])

	if 'resume' not in request.files:
		flash('No selected file')
		return redirect(url_for('profile'))

	resume = request.files['resume']
	# check if a file is selected
	if resume.filename =='':
		flash('No selected file')
		return redirect(url_for('profile'))

	# TODO check it is the correct type of file
	if resume:
		filename = secure_filename(resume.filename)
		data = resume.read()

		student.filename = filename
		student.resume = data
		
		db.session.commit()
		db.session.flush()


		print("SAVED")

	return redirect(url_for('profile'))


@app.route('/resume/<int:id>')
def download_resume(id):
	res = Student.query.get(id).resume
	filename = Student.query.get(id).filename
	print(filename, flush=True)

	if not res:
		print("Warn: No resume",flush=True)
		flash('This resume does not exist')
		return redirect(request.referrer)
	else:
		return send_file(io.BytesIO(res),
					 mimetype='application/octet-stream')


@app.route('/organization/<int:id>')
def organization(id):
	# if not logged in
	if not g.user:
		return redirect(url_for('login'))
	organization = Organization.query.get(id)

	# Probably very inefficient, but 
	return render_template('org.html',
						   organization=Organization.query.get(id),
						   student_query=Student.query)

@app.route('/company/<int:id>')
def company(id):
	# if not logged in
	if not g.user:
		return redirect(url_for('login'))
	comp = Company.query.get(id)
	
	return render_template('comp.html',
						   company=comp)


@app.route('/delete_user/<int:id>', methods=['POST'])
def delete_user(id):
	user = User.query.get(id)
	if not user:
		flash('This user does not exist')
	
	db.session.delete(user)
	db.session.commit()
	flash('The user was successfully deleted')

	return redirect(url_for('root'))


@app.route('/delete_company/<int:id>', methods=['POST'])
def delete_company(id):
	company = Company.query.get(id)
	if not company:
		flash('This company does not exist')

	organization = Organization.query.get(g.user.id)
	if not organization:
		flash('This company does not exist')

	# Assume that `g.user` is the organization user who is removing a company
	organization.companies.remove(company)
	db.session.commit()
	flash('The company was successfully deleted')

	return redirect(url_for('root'))


# Routes to approve/reject a student or company organization join request
# Implementing these as separate routes (probably inefficient) due to the time constraint 
@app.route('/approve_student_request/<int:id>', methods=['POST'])
def approve_student_request(id):
	student = Student.query.get(id)
	if not student:
		flash('This student does not exist')
	
	# Assume that `g.user` is the organization account to approve this request for easier implementation
	organization = Organization.query.get(g.user.id)
	if not organization:
		flash('This organization does not exist')
	
	student.pending_organizations.remove(organization)
	student.organizations.append(organization)
	db.session.commit()
	flash('The student was successfully added to your organization!')

	return redirect(url_for('organization', id=organization.id))


@app.route('/reject_student_request/<int:id>', methods=['POST'])
def reject_student_request(id):
	student = Student.query.get(id)
	if not student:
		flash('This student does not exist')
	
	# Assume that `g.user` is the organization account to approve this request for easier implementation
	organization = Organization.query.get(g.user.id)
	if not organization:
		flash('This organization does not exist')
	
	student.pending_organizations.remove(organization)
	db.session.commit()
	# TODO: Deliver rejection notification?

	return redirect(url_for('organization', id=organization.id))


@app.route('/approve_company_request/<int:id>', methods=['POST'])
def approve_company_request(id):
	company = Company.query.get(id)
	if not company:
		flash('This company does not exist')
	
	# Assume that `g.user` is the organization account to approve this request for easier implementation
	organization = Organization.query.get(g.user.id)
	if not organization:
		flash('This organization does not exist')
	
	company.pending_organizations.remove(organization)
	company.organizations.append(organization)
	db.session.commit()
	flash('The company was successfully added to your organization!')

	return redirect(url_for('organization', id=organization.id))


@app.route('/reject_company_request/<int:id>', methods=['POST'])
def reject_company_request(id):
	company = Student.query.get(id)
	if not company:
		flash('This company does not exist')
	
	# Assume that `g.user` is the organization account to approve this request for easier implementation
	organization = Organization.query.get(g.user.id)
	if not organization:
		flash('This organization does not exist')
	
	company.pending_organizations.remove(organization)
	db.session.commit()
	# TODO: Deliver rejection notification?

	return redirect(url_for('organization', id=organization.id))


@app.route('/help')
def help():
	return render_template('help.html')

@app.route('/apply_filter')
def apply_filter():
	return redirect(url_for('organization', id=organization.id, stud=organization.students))

# Get the student profile
@app.route('/student/<int:id>', methods=['GET'])
def student(id):
	student = Student.query.get(id)
	if not student:
		flash('This student does not exist')
	
	data = {}
	data['id'] = student.id
	data['first_name'] = student.first_name
	data['last_name'] = student.last_name
	data['year'] = student.year.value
	data['major'] = student.major
	data['minor'] = student.minor
	data['grade'] = student.year.value
	data['gender'] = student.gender.value
	data['gpa'] = student.gpa
	data['phone_number'] = student.phone

	return jsonify(data)
