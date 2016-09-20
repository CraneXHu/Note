from __future__ import with_statement
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from contextlib import closing
import datetime

#configuration
DATABASE = '.\\tmp\\notes.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
	return sqlite3.connect(app.config['DATABASE'])

def init_db():
	with closing(connect_db()) as db:
		with app.open_resource('schema.sql') as f:
			db.cursor().executescript(f.read())
		db.commit()

@app.before_request
def before_request():
	g.db = connect_db()

@app.after_request
def after_request(response):
	g.db.close()
	return response

@app.route('/')
def home():
	if session.get('logged_in'):
		cur = g.db.execute('select time, content from notes order by id desc')
		notes = [dict(time=row[0],content=row[1]) for row in cur.fetchall()]
		return render_template('home.html',notes=notes)
	else:
		return render_template('login.html')

@app.route('/create', methods=['POST'])
def create_note():
	if not session.get('logged_in'):
		abort(401)
	now = datetime.datetime.now()
	time = now.strftime('%Y-%m-%d %H:%M:%S');
	g.db.execute('insert into notes (time, content) values (?, ?)',
                 [time, request.form['content']])
	g.db.commit()
	return time

@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		if request.form['account'] != app.config['USERNAME']:
			error = 'Invalid username'
		elif request.form['password'] != app.config['PASSWORD']:
			error = 'Invalid password'
		else:
			session['logged_in'] = True
			return redirect(url_for('home'))
	return render_template('login.html',error=error)

@app.route('/logout')
def logout():
	session.pop('logged_in')
	flash('You were logged out')
	return redirect(url_for('home'))

if __name__ == '__main__':
	app.run()