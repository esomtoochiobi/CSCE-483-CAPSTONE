from db import create_user, get_user_by_id, get_user_by_email
from dotenv import load_dotenv
from flask import flash, Flask, request, render_template, redirect, url_for
from flask_bcrypt import Bcrypt
from user import User

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
    return get_user_by_id(user_id)

# Routes
@app.route('/')
def howdy_world():
    return render_template('index.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if flask_login.current_user.is_authenticated:
        return 'You are already registered.'

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if get_user_by_email(email) != None:
            return 'That email is already in use.'

        create_user(email, bcrypt.generate_password_hash(password))
    
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask_login.current_user.is_authenticated:
        return 'You are already logged in.'

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = get_user_by_email(email)

        if bcrypt.check_password_hash(user.password, password):
            flask_login.login_user(user)
            return redirect(url_for('profile'), code=303)

        return 'Invalid login!'
    
    return render_template('login.html')  

@app.route('/logout')
@flask_login.login_required
def logout():
    flask_login.logout_user()
    flash('You are logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/profile')
@flask_login.login_required
def profile():
    return f'Howdy, {flask_login.current_user.email}'