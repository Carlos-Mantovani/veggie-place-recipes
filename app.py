from flask import Flask, render_template, request, redirect, session, flash
import mysql.connector
from settings import DATABASE_PASSWORD
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import secrets
import random
from werkzeug.utils import secure_filename
import os

db = mysql.connector.connect(
	host='localhost',
	user='root',
	password=DATABASE_PASSWORD,
	database='veggie_place'
)

cursor = db.cursor(dictionary=True)

UPLOAD_FOLDER = os.getcwd() + '/static/photos'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

print(UPLOAD_FOLDER)

app = Flask(__name__)
app.secret_key=secrets.token_urlsafe(random.randrange(16, 256))
app.permanent_session_lifetime = timedelta(days=5)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
	return '.' in filename and \
		filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
	if 'user' in session:
		user = session['user']
		print(user)
		return render_template('index.html', user=user)
	return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == 'POST':
		username = request.form.get('username')
		email = request.form.get('email')
		password = request.form.get('password')
		confirmation = request.form.get('confirmation')
		if not username or not email or not password or not confirmation:
			return render_template('register.html', message='You must fill in all the inputs')
		elif password != confirmation:
			return render_template('register.html', message='Passwords does not match')
		else:
			cursor.execute('SELECT * FROM users WHERE email = %s', (email, ))
			user = cursor.fetchall()
			if len(user) > 0:
				return render_template('register.html', message='Email already registered')
			password_hash = generate_password_hash(password)
			print(password_hash)
			cursor.execute('INSERT INTO users (username, email, password, created_at) VALUES (%s, %s, %s, %s)', (username, email, password_hash, datetime.now()))
			db.commit()
			return render_template('register.html', message='Registered with sucess!')

	if request.method == 'GET':
		return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		if 'user' in session:
			return redirect('/')
		email = request.form.get('email')
		password = request.form.get('password')
		if not email or not password:
			return render_template('login.html', message='You must fill in all the inputs')
		cursor.execute('SELECT * FROM users WHERE email = %s', (email, ))
		try:
			user = cursor.fetchall()[0]
			password_hash = user['password']
			if check_password_hash(password_hash, password):
				session.permanent = True
				session['user'] = user
				return redirect('/')
			else:
				return render_template('login.html', message='Incorrect username or password')
		except IndexError:
			return render_template('login.html', message='Incorrect username or password')
		
	if request.method == 'GET':
		return render_template('login.html')

@app.route('/logout')
def logout():
	session.pop('user', None)
	return redirect('/login')

@app.route('/user/<id>')
def show_user(id):
	cursor.execute('SELECT * FROM users WHERE id = %s', (id, ))
	user_shown = cursor.fetchall()[0]
	if 'user' in session:
		user = session['user']
		if int(id) == session['user']['id']:
			logged_in = True
			return render_template('user.html', user_shown=user_shown, user=user, logged_in=logged_in)
		return render_template('user.html', user_shown=user_shown, user=user)
	return render_template('user.html', user_shown=user_shown)

@app.route('/edit', methods=['POST'])
def edit_user():
	try:
		user = session['user']
		print(request.form)
		print(request.files)
		if not request.form.get('password') and 'picture' not in request.files:
			new_username = request.form.get('username')
			cursor.execute('UPDATE users SET username=%s WHERE id=%s', (new_username, user['id']))
			db.commit()
		elif 'picture' not in request.files and not request.form.get('password'):
			new_username = request.form.get('username')
			cursor.execute('UPDATE users SET username=%s WHERE id=%s', (new_username, user['id']))
			db.commit()
		elif not request.form.get('password') and not request.form.get('username'):
			picture = request.files['picture']
			print(picture.filename)
			if picture.filename == '':
				print('a')
				flash('no selected file')
				return redirect(f'/user/{user["id"]}')
			if picture and allowed_file(picture.filename):
				filename = secure_filename(str(user['id']) + '.' + picture.filename.rsplit('.', 1)[1].lower())
				picture.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
				return redirect(f'/user/{user["id"]}')
		elif 'username' not in request.form and 'picture' not in request.files:
			new_password = request.form.get('password')
			new_password_hash = generate_password_hash(new_password)
			cursor.execute('UPDATE users SET password=%s WHERE id=%s', (new_password_hash, user['id']))
			db.commit()
		else:
			username = request.form.get('username')
			password = request.form.get('password')
			picture = request.files['picture']
			if username == '' or password == '' or picture == '':
				return redirect(f'/user/{user["id"]}')
			new_username = request.form.get('username')
			new_password = request.form.get('password')
			new_password_hash = generate_password_hash(new_password)
			cursor.execute('UPDATE users SET username=%s, password=%s WHERE id=%s', (new_username, new_password_hash, user['id']))
			db.commit()
			picture = request.files['picture']
			if picture.filename == '':
				flash('no selected file')
				return redirect(f'/user/{user["id"]}')
			if picture and allowed_file(picture.filename):
				filename = secure_filename(user['id'] + filename.rsplit('.', 1)[1].lower())
				print(filename)
				picture.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
				return redirect(f'/user/{user["id"]}')
		return redirect(f'/user/{user["id"]}')
	except:
		return redirect(f'/user/{user["id"]}')