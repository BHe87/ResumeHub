from flask import Flask, redirect, render_template, url_for, g, session, request, abort, flash, make_response, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug import check_password_hash, generate_password_hash, secure_filename

from model import Company, db, Gender, Organization, Student, User, Year
from werkzeug.datastructures import FileStorage

import os, io
from base64 import b64encode

# init
app = Flask(__name__)

app.config.update(dict(
	SECRET_KEY='GROUP18_RESUMEHUB',
	USERNAME='admin',
	PASSWORD='greatpassword',
	SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.root_path, 'resumehub.db')
))

db.init_app(app)


@app.cli.command('initdb')
def initdb_command():
	# Drop the database and create the new one
	db.drop_all()
	db.create_all()

	# hardcode organization(s)
	db.session.add(Organization(username='Fresa',
								pw_hash=generate_password_hash('fresa'),
								email='Fresa@pitt.edu',
								first_name='Fresa',
								last_name='Fresa',
								description='Dance together!'))
	db.session.add(Organization(username='KSA',
								pw_hash=generate_password_hash('ksa'),
								email='KSA@pitt.edu',
								first_name='KSA',
								last_name='KSA',
								description='Koreans squads!'))
	db.session.add(Organization(username='ASA',
								pw_hash=generate_password_hash('asa'),
								email='ASA@pitt.edu',
								first_name='ASA',
								last_name='ASA',
								description='Asian squads!'))
	db.session.add(Organization(username='WiCS',
								pw_hash=generate_password_hash('wics'),
								email='WiCS@pitt.edu',
								first_name='WiCS',
								last_name='WiCS',
								description='Women in CS!'))
	db.session.add(Organization(username='GlobalTie',
								pw_hash=generate_password_hash('globaltie'),
								email='GlobalTie@pitt.edu',
								first_name='GlobalTie',
								last_name='GlobalTie',
								description='Global Tie!'))
	db.session.commit()
	print('Initialized the database')


@app.before_request
def before_request():
	g.user = None
	if 'user_id' in session:
		g.user = User.query.get(session['user_id'])


@app.route('/')
def root():
	# if not logged in
	if not g.user:
		return redirect(url_for('login'))
	
	orgs = Student.query.get(session['user_id']).organizations
	return render_template('index.html',
							organizations=orgs)
	

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
			session['user_id'] = user.id
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


@app.route('/register', methods=['GET', 'POST'])
def register():
	# if already logged in
	if g.user:
		return redirect(url_for('index'))
	
	error = None
	if request.method == 'POST':
		if not request.form['username']:
			error = 'Please, enter a username'
		elif not request.form['password']:
			error = 'Please, enter a password'
		elif request.form['password'] != request.form['password2']:
			error = 'Passwords do not match!'
		elif not request.form['firstName']:
			error = 'Please, enter a first name'
		elif not request.form['lastName']:
			error = 'Please, enter a last name'
		# TODO: check username and email constraints
		# elif User.query.filter_by(username=request.form['username']).first():
		# 	error = request.form['username'] + ' - This username is in use'
		# elif User.query.filter_by(email=request.form['email']).first():
		# 	error = request.form['email'] + ' - This email is in use'
		else:
			print('You were successfully registered!')
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
						   orgniazations=Organization.query.all(),
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