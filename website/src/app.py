from bokeh.plotting import figure, save, output_file
from client import get_soil_moisture_data, get_valve_data, update_valve_data
from db import create_hub, create_sensor, create_reading, create_user, delete_device_by_id, get_user_by_id, get_user_by_email, get_sensors_by_user, get_hubs_by_user, get_readings_for_device, update_device_threshold
from dotenv import load_dotenv
from flask import flash, Flask, request, render_template, redirect, url_for
from flask_bcrypt import Bcrypt
from flask_rq2 import RQ
from entities.user import User
from redis import Redis
from rq_scheduler import Scheduler

import flask_login
import os
import time

# Load env variables
load_dotenv()

# Create app and login manager
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.config['REDIS_URL'] = 'redis://localhost:6379/0'

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

bcrypt = Bcrypt(app)

# Setup Flask-RQ2
redis = Redis()
rq = RQ(app, connection=redis)

scheduler = Scheduler(connection=redis)

# Set up way to load users into a session
@login_manager.user_loader
def load_user(user_id):
    user = get_user_by_id(user_id)
    user.hubs = get_hubs_by_user(user_id)
    user.sensors = get_sensors_by_user(user_id)
    return user

@rq.job
def push_data_to_db(user_id):
    print(f"Job executed at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    user = load_user(user_id)
    moisture_data = get_soil_moisture_data(user.sensors)

    for hub in user.hubs:
        for sensor in user.sensors[hub.id][1]:
            create_reading(sensor.id, moisture_data[hub.id][1][sensor.id])

        for sensor in user.sensors[hub.id][2]:
            create_reading(sensor.id, moisture_data[hub.id][2][sensor.id])

    print(f"Job finished at {time.strftime('%Y-%m-%d %H:%M:%S')}")

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
    moisture_data = get_soil_moisture_data(flask_login.current_user.sensors)
    valve_data = get_valve_data(flask_login.current_user.hubs)

    for hub in flask_login.current_user.hubs:
        # Handle zone 1
        for sensor in flask_login.current_user.sensors[hub.id][1]:
            if moisture_data[hub.id][1][sensor.id] < hub.thresholds[0]:
                flash(f'Sensor_{sensor.id} is under threshold')
        # Handle zone 2
        for sensor in flask_login.current_user.sensors[hub.id][2]:
            if moisture_data[hub.id][2][sensor.id] < hub.thresholds[1]:
                flash(f'Sensor_{sensor.id} is under threshold')
    
    listofjobs = scheduler.get_jobs()
    schedule_job = True

    for job in listofjobs:
        if flask_login.current_user.id == job.meta['id']:
            print('no schedule')
            schedule_job = False

    if schedule_job:
        scheduler.cron('*/1 * * * *', func=push_data_to_db, args=[flask_login.current_user.id], meta={'id': flask_login.current_user.id})

    return render_template('profile.html', user=flask_login.current_user, data=moisture_data, valve_data=valve_data)

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

@app.route('/create_hub', methods=['GET', 'POST'])
@flask_login.login_required
def createhub():
    if request.method == 'POST':
        thing_id = request.form.get('thing_id')
        soil_1 = int(request.form.get('soil_type_1'))
        soil_2 = int(request.form.get('soil_type_2'))
        create_hub(flask_login.current_user.id, thing_id, soil_1, soil_2)

        return 'Please close this tab.'
    else:
        return(render_template('create_hub.html'))

@app.route('/create_sensor', methods=['GET', 'POST'])
@flask_login.login_required
def createsensor():
    if request.method == 'POST':
        thing_id = request.form.get('thing_id')
        hub_id = int(request.form.get('hub_id'))
        zone = int(request.form.get('zone'))
        create_sensor(thing_id, hub_id, zone)

        return 'Please close this tab.'
    else:
        return(render_template('create_sensor.html', user=flask_login.current_user))   

@app.route('/update_threshold', methods=['POST'])
@flask_login.login_required
def update_threshold():
    device_id = request.form.get('device_id')
    threshold = request.form.get('threshold')
    zone = request.form.get('zone')

    update_device_threshold(device_id, threshold, zone)

    return redirect(url_for('profile'))

@app.route('/update_valves', methods=['POST'])
@flask_login.login_required
def update_valves():
    device_id = int(request.form.get('device_id'))
    device = next(device for device in flask_login.current_user.hubs if device.id == device_id)
    
    valve1 = request.form.get('valve1') != None
    valve2 = request.form.get('valve2') != None

    valve_data = get_valve_data([device]) 
    print(device_id)
    print(valve_data)
    print(valve1, valve2)

    if valve1 ^ valve_data[device.id][0]:
        print('1')
        update_valve_data(device, 0, valve1)

    if valve2 ^ valve_data[device.id][1]:
        print(2)
        update_valve_data(device, 1, valve2)

    return redirect(url_for('profile'))
