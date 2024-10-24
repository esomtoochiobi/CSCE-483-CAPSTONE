from db import create_user, get_user_by_id, get_user_by_email, get_devices_by_user
from dotenv import load_dotenv
from flask import flash, Flask, request, render_template, redirect, url_for
from flask_bcrypt import Bcrypt
from user import User
import threading

import os
import flask_login

# Load env variables
load_dotenv()

# Create app and login manager
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

bcrypt = Bcrypt(app)

# Set up way to load users into a session
@login_manager.user_loader
def load_user(user_id):
    user = get_user_by_id(user_id)
    user.devices = get_devices_by_user(user_id)
    return user

# Routes
@app.route('/')
def index():
    get_devices_by_user(flask_login.current_user.id)
    return render_template('index.html')

@app.route('/register', methods=['GET','POST'])
def register():
    error = None

    if flask_login.current_user.is_authenticated:
        return 'You are already registered.'

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if get_user_by_email(email) != None:
            error = 'That email is already in use.'
        else:
            create_user(email, bcrypt.generate_password_hash(password))
            flash('You are registered.')
            return redirect(url_for('login'))
    
    return render_template('register.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if flask_login.current_user.is_authenticated:
        return 'You are already logged in.'

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = get_user_by_email(email)

        if user and bcrypt.check_password_hash(user.password, password):
            flask_login.login_user(user)
            flash('You are logged in.')
            return redirect(url_for('profile'), code=303)
        else:
            error = 'Invalid login!'
    
    return render_template('login.html', error=error)  

@app.route('/logout')
@flask_login.login_required
def logout():
    flask_login.logout_user()
    flash('You are logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/profile')
@flask_login.login_required
def profile():
    for i in range(len(flask_login.current_user.devices)):
        flask_login.current_user.devices[i].client.start()
    return render_template('profile.html', user=flask_login.current_user)

# Unauthorized error handling
@app.errorhandler(401)
def page_not_found(e):
    return render_template('error.html')