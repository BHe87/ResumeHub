from flask import Flask, redirect, render_template, url_for, g, session, request, abort, flash, make_response, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug import check_password_hash, generate_password_hash, secure_filename

from model import Company, db, Gender, Organization, Student, User, Year, WorkStatus, Clearance, SearchStatus
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
						   phone='123456789'))

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
		# A user is logged in as Company
		else:
			g.user = Company.query.get(session['user_id'])


@app.route('/')
def root():
	# if not logged in
	if not g.user:
		return redirect(url_for('login'))
	
	organizations = None
	if type(g.user) is Student:
		organizations = g.user.organizations
	# will display the own organization info; therefore, no need to assign `organizations`
	elif type(g.user) is Organization:
		print('TODO: Do whatever we need here')
	else:
		# TODO: assign appropriate organizations 
		raise NotImplementedError("TODO: Pass different arguments if the current user is Company")
	
	return render_template('index.html',
							organizations=organizations) 
	

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
				error = 'Please, enter a valid phone number'
			elif not request.form['GPA']:
				error = 'Please, enter a GPA'
			else:
				print('Your student account was successfully registered!')
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
			elif request.form['password'] != request.form['password2']:
				error = 'Passwords do not match!'
			elif not request.form['email']:
				error = 'Please, enter an email'
			elif not request.form['organizationName']:
				error = 'Please, enter an organization name'
			else:
				print('Your student organization account was successfully registered!')
				db.session.add(Organization(username=request.form['username'],
									pw_hash=generate_password_hash(request.form['password']),
									email=request.form['email'],
									name=request.form['organizationName']))
				db.session.commit()
				return redirect(url_for('login'))

		#elif user_type == 'Company':

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
	current_student = Student.query.get(session['user_id'])
	
	resume = None
	if current_student.resume is not None:
		resume = b64encode(current_student.resume)

	return render_template('profile.html',
						   current_student=current_student,
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
	current_student = Student.query.get(session['user_id'])
	# check if a student has already joined the organization;
	# TODO: Remove this, and add UniqueConstraint to `organizations` in model.py in order to handle this properly
	if organization in current_student.organizations:
		return redirect(url_for('profile'))

	current_student.organizations.append(organization)
	db.session.commit()

	return render_template('student_submission.html', result='true')


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


@app.route('/resume/<filename>')
def download_resume(filename):
	res = Student.query.get(session['user_id']).resume
	filename = Student.query.get(session['user_id']).filename
	print(filename, flush=True)

	if not res:
		print("Warn: No resume",flush=True)
		flash('Your resume does not exist')
		return redirect(url_for('profile'))
	else:
		return send_file(io.BytesIO(res),
					 mimetype='application/octet-stream')


@app.route('/organization/<int:id>')
def organization(id):
	# if not logged in
	if not g.user:
		return redirect(url_for('login'))
	organization = Organization.query.get(id)
	
	return render_template('org.html',
						   organization=Organization.query.get(id))