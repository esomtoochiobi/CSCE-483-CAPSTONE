from dotenv import load_dotenv
from flask import Flask, request, render_template
from user import User
from db import create_user, get_user_by_id, get_user_by_email

import os
import flask_login


load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(user_id)


@app.route('/')
def howdy_world():
    return '<h1>Howdy, world!</h1>'


@app.route('/register', methods=['POST'])
def register_user():
    email = request.form.get('email')
    password = request.form.get('password')
    create_user(email, password)
   
    return 'REGISTERED!'


@app.route('/login', methods=['POST'])
def login_user():
    email = request.form.get('email')
    password = request.form.get('password')

    if password == get_user_by_email(email):
        return 'Welcome!'
    return 'Invalid login!'