from bokeh.plotting import figure, save, output_file
from db import create_device, create_user, get_user_by_id, get_user_by_email, get_devices_by_user, get_readings_for_device
from dotenv import load_dotenv
from flask import flash, Flask, request, render_template, redirect, url_for
from flask_bcrypt import Bcrypt
from entities.user import User
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
    return render_template('index.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if flask_login.current_user.is_authenticated:
        return render_template('error_loggedin.html') 

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if get_user_by_email(email) != None:
            flash('That email is already in use.')
        else:
            create_user(email, bcrypt.generate_password_hash(password))
            flash('You are registered.')
            return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask_login.current_user.is_authenticated:
        return render_template('error_loggedin.html')

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = get_user_by_email(email)

        if user and bcrypt.check_password_hash(user.password, password):
            flask_login.login_user(user)
            flash('You are logged in.')
            return redirect(url_for('profile'), code=303)
        else:
            flash('Invalid login credentials.')
    
    return render_template('login.html')  

@app.route('/logout')
@flask_login.login_required
def logout():
    flask_login.logout_user()
    flash('You are logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/profile', methods=['GET', 'POST'])
@flask_login.login_required
def profile():
    if request.method == 'POST':
        device_key = request.form.get('device_key')
        device_id = request.form.get('device_id')
        device_type = request.form.get('device_type')
        soil_type = request.form.get('soil_type')

        create_device(flask_login.current_user.id, device_key, device_id, device_type, soil_type)
        return redirect(url_for('profile')) 

    for i in range(len(flask_login.current_user.devices)):
        flask_login.current_user.devices[i].client.start()

    return render_template('profile.html', user=flask_login.current_user)

# Unauthorized error handling
@app.errorhandler(401)
def page_not_found(e):
    return render_template('error.html')

@app.route('/soil_graph', methods=['POST'])
@flask_login.login_required
def soil_graph():
    start_date = request.form.get('start').replace('T', ' ') + ':00'
    end_date = request.form.get('end').replace('T', ' ') + ':00'

    readings = get_readings_for_device(5, start_date, end_date)

    output_file(f'templates/graphs/soil_{flask_login.current_user.id}_graph.html')

    plot = figure(title='Soil Moisture Plot', x_axis_label='Timestamps', y_axis_label='Soil Moisture (%)', x_range=[reading.last_time for reading in readings])
    plot.vbar(x=[reading.last_time for reading in readings], top=list(reading.value for reading in readings), width=0.5, legend_label='Sensor_5')

    plot.xgrid.grid_line_color = None
    plot.y_range.start = 0

    plot.xaxis.major_label_orientation = "vertical"

    save(plot)

    return render_template(f'graphs/soil_{flask_login.current_user.id}_graph.html')

