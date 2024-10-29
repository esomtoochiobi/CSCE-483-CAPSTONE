from dotenv import load_dotenv
from user import User

import os
import pymysql.cursors

load_dotenv()

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = int(os.getenv('DB_PORT'))

# Define method to generate a connection to the DB
def get_connection(): 
    return pymysql.connect(host=DB_HOST,
                           user=DB_USER, 
                           passwd=DB_PASS, 
                           port=DB_PORT, 
                           db=DB_NAME)

# Define method to create user given email and password
def create_user(email: str, password: str):
    with get_connection() as cnx:
        with cnx.cursor() as cursor:
            sql = "INSERT INTO `users` (`email`, `password`) VALUES (%s, %s)"
            cursor.execute(sql, (email, password))
        
        cnx.commit()

# Define method to get user by email from database
def get_user_by_email(email: str) -> User:
    with get_connection().cursor() as cursor:
        sql = "SELECT * FROM `users` WHERE `email` = %s"
        cursor.execute(sql, (email))
        
        return None if (user := cursor.fetchone()) == None else User(user[0], user[1], user[2])

# Define method to get user by id from database
def get_user_by_id(user_id: str) -> User:
    with get_connection().cursor() as cursor:
        sql = "SELECT * FROM `users` WHERE `id` = %(id)s"
        cursor.execute(sql, args={'id': int(user_id)})

        return None if (user := cursor.fetchone()) == None else User(user[0], user[1], user[2])

# Define method to add device to database
def create_device(user_id: str, device_key: str, device_id: str, device_type: str):
    with get_connection() as cnx:
        with cnx.cursor() as cursor:
            sql = "INSERT INTO `devices` (`user_id`, `device_key`, `device_id`, `device_type`) VALUES (%(ui)s, %(dk)s, %(di)s, %(dt)s)"
            cursor.execute(sql, args={'ui': int(user_id), 'dk': device_key, 'di': device_id, 'dt': int(device_type)})
        
        cnx.commit()

# Define method to get devices by user_id from database
def get_devices_by_user(user_id: str): 
    from devices import Hub, Sensor
    with get_connection().cursor() as cursor:
        sql = "SELECT * FROM `devices` WHERE `user_id` = %(id)s"
        cursor.execute(sql, args={'id': int(user_id)})

        devices = []

        for device in cursor:
            if device[4] == 0:      # Sensor
                devices.append(Sensor(device[0], device[2], device[3], device[4], device[5], device[6], device[8]))
            else:                   # Hub
                devices.append(Hub(device[0], device[2], device[3], device[4], device[7]))


        print(f'{len(devices)} devices found')
        return devices

def update_soil_moisture(device_id: str, moisture: str):
    with get_connection() as cnx:
        with cnx.cursor() as cursor:
            sql = "UPDATE `devices` SET moisture = %(m)s, last_time_updated = NOW() WHERE `id` = %(id)s"
            cursor.execute(sql, args={'id': device_id, 'm': moisture})

        cnx.commit()
        