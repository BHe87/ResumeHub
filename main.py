from flask import Flask, redirect, render_template, url_for
from flask_sqlalchemy import SQLAlchemy

from model import Company, db, Gender, Organization, Student, Year

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
	print('Initialized the database')


@app.route('/')
def root():
	#return render_template('sign-in.html')
	return render_template('index.html')
	

@app.route('/sign-in')
def signIn():
	return render_template('sign-in.html')


@app.route('/home')
def home():
	return render_template('home.html')


@app.route('/profile')
def profile():
	return render_template('profile.html',
						   YEAR=Year,
						   GENDER=Gender)

@app.route('/save_profile', methods=['POST'])
def save_profile():
	# TODO: Save tidbits accordingly
	return redirect(url_for('profile'))