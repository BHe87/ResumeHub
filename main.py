from flask import Flask, redirect, render_template, url_for, g, session, request, abort, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug import check_password_hash, generate_password_hash

from model import Company, db, Gender, Organization, Student, User, Year

import os

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

	# Add admin account

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
	
	return render_template('index.html')
	

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


@app.route('/home')
def home():
	return render_template('home.html')


@app.route('/profile')
def profile():

	# Check if user is not logged in. SKIP FOR NOW
	#if not g.user:
	#	return redirect(url_for('login'))

	# FOR TESTING 
	# TODO Take out hardcoded test, and use real user profile
	stud = Student()
	stud.first_name = "LOL"
	stud.last_name = "GG"
	stud.gpa = 5.0

	return render_template('profile.html',
						   STUDENT=stud,
						   YEAR=Year,
						   GENDER=Gender)


@app.route('/save_profile', methods=['POST'])
def save_profile():
	# TODO: Save tidbits accordingly
	# Check if logged in - doesn't currently work
	student = None

	# if not g.user:
	# 	return redirect(url_for('login'))
	# else:

	# TODO Use real user account instead of Hardcoded student 
	student = Student() #User.query.filter_by(username=User.username).first() # Not sure if this is correct
	student.first_name = "Hey"
	print(student.first_name)

	if student == None:
		print("Error: Student in NULL when saving profile", flush=True)

	# Collect which fields we are missing
	warn = ""

	# Check we have stuff for each field
	# Ideally we auto fill the info they already have?
	if request.method == 'POST':
		print("POST", flush=True)
		for key in request.form.lists():
			print(key)

		if not request.form['resume']:
			warn += "Missinng resume\n"
		else:
			print("Definitely adding the resume: {} ".format(request.form['resume']))
			student.resume = request.form.getlist('resume')[0]

		if not request.form['first-name']:
			warn += "Missing name\n"
		else:
		 	student.first_name = request.form.getlist('first-name')[0] # just use first name for now lol

		if not request.form['last-name']:
			warn += "Missing name\n"
		else:
		 	student.first_name = request.form.getlist('last-name')[0] # just use first name for now lol

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
		print("Updating profile...")


	print("Ayy got it boss")
	return redirect(url_for('profile'))