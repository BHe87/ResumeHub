from flask import Flask, render_template
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
	return render_template('index.html')


@app.route('/profile')
def profile():
	return render_template('profile.html',
						   YEAR=Year,
						   GENDER=Gender)