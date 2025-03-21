from flask import Flask, render_template, request, redirect, session, flash
import mysql.connector
from dev_settings import DATABASE_PASSWORD
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
            cursor.execute('INSERT INTO users (username, email, password, created_at, updated_at) VALUES (%s, %s, %s, %s, %s)', (username, email, password_hash, datetime.now(), datetime.now()))
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
        print(user)
        if int(id) == session['user']['id']:
            logged_in = True
            return render_template('user.html', user_shown=user_shown, user=user, logged_in=logged_in)
        return render_template('user.html', user_shown=user_shown, user=user)
    return render_template('user.html', user_shown=user_shown)

@app.route('/edit', methods=['POST'])
def edit_user():
    try:
        user = session['user']

        username = request.form.get('username')
        password = request.form.get('password')
        picture = request.files['picture']
        print(request.form)
        print(request.files)
        if not password and not picture:
            new_username = request.form.get('username')
            cursor.execute('UPDATE users SET username=%s WHERE id=%s', (new_username, user['id']))
            db.commit()
        #elif not picture and not password:
        #   new_username = request.form.get('username')
        #   cursor.execute('UPDATE users SET username=%s WHERE id=%s', (new_username, user['id']))
        #   db.commit()
        elif not password and not username:
            picture = request.files['picture']
            print(picture.filename)
            if picture.filename == '':
                flash('no selected file')
                return redirect(f'/user/{user["id"]}')
            if picture and allowed_file(picture.filename):
                filename = secure_filename(str(user['id']) + '.' + picture.filename.rsplit('.', 1)[1].lower())
                picture.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return redirect(f'/user/{user["id"]}')
        elif not username and not picture:
            new_password = request.form.get('password')
            new_password_hash = generate_password_hash(new_password)
            cursor.execute('UPDATE users SET password=%s, updated_at=%s WHERE id=%s', (new_password_hash, datetime.now(), user['id']))
            db.commit()
        else:
            if not username or not password or not picture:
                return redirect(f'/user/{user["id"]}')
            new_username = request.form.get('username')
            print(new_username)
            new_password = request.form.get('password')
            new_password_hash = generate_password_hash(new_password)
            cursor.execute('UPDATE users SET username=%s, password=%s, updated_at WHERE id=%s', (new_username, new_password_hash, datetime.now(), user['id']))
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

@app.route('/register_recipe', methods=['GET', 'POST'])
def register_recipe():
    if request.method == 'GET':
        if 'user' in session:
            user = session['user']
            return render_template('register_recipe.html', user=user)
        else:
            return redirect('/login')
    if request.method == 'POST':
        #try:
        user = session['user']
        print('a')
        title = request.form.get('recipe-name')
        description = request.form.get('description')
        ingredients = request.form.get('ingredients')
        instructions = request.form.get('instructions')
        prep_time = request.form.get('prep-time')
        cook_time = request.form.get('cook-time')
        category = request.form.get('category')
        if not title or not description or not ingredients or not instructions or not prep_time or not cook_time or not category:
            print('b')
            return render_template('register-recipe.html', user=user, message='You must fill in all the inputs')
        print(user['id'])
        cursor.execute('INSERT INTO recipes (user_id, title, description, ingredients, instructions, prep_time, cook_time, category, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (user['id'], title, description, ingredients, instructions, prep_time, cook_time, category, datetime.now(), datetime.now()))
        db.commit()
        print('d')
        return redirect(f'/user/{user["id"]}')
        #except:
            #return redirect(f'/user/{user["id"]}')
