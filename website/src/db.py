from dotenv import load_dotenv
from entities.user import User
from entities.reading import Reading

import os
import pymysql.cursors

load_dotenv()

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = int(os.getenv('DB_PORT'))

SOIL_VALUES = [10, 16, 21, 27, 30, 36, 32, 29, 28, 40, 40]

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

# Define method to add sensor to database
def create_device(user_id: str, device_id: str, device_type: int, soil_type: int):
    with get_connection() as cnx:
        with cnx.cursor() as cursor:
            sql = "INSERT INTO `devices` (`user_id`, `thing_id`, `device_type`, `soil_threshold`, `soil_type`) VALUES (%(ui)s, %(di)s, %(dt)s, %(t)s, %(st)s)"
            cursor.execute(sql, args={'ui': int(user_id), 'di': device_id, 'dt': device_type, 't': SOIL_VALUES[int(soil_type)], 'st': soil_type})
        
        cnx.commit()

# Define method to add a hub to database
def create_hub(user_id: int, thing_id: str, soil_type_1: int, soil_type_2: int):
    with get_connection() as cnx:
        with cnx.cursor() as cursor:
            sql = "INSERT INTO `hubs` (`user_id`, `thing_id`, `soil_type_1`, `soil_type_2`, `threshold1`, `threshold2`) VALUES (%(ui)s, %(ti)s, %(s1)s, %(s2)s, %(t1)s, %(t2)s)"
            cursor.execute(sql, args={'ui': user_id, 'ti': thing_id, 's1': soil_type_1, 's2': soil_type_2, 't1': SOIL_VALUES[soil_type_1], 't2': SOIL_VALUES[soil_type_2]})

        cnx.commit()

# Define method to add a sensor to database
def create_sensor(thing_id: str, hub_id: int, zone: int):
    with get_connection() as cnx:
        with cnx.cursor() as cursor:
            sql = "INSERT INTO `sensors` (`thing_id`, `hub_id`, `zone`) VALUES (%(ti)s, %(hi)s, %(z)s)"
            cursor.execute(sql, args={'ti': thing_id, 'hi': hub_id, 'z': zone})

        cnx.commit()

# Define method to retrieve hubs from database
def get_hubs_by_user(user_id: int):
    from entities.devices import Hub
    with get_connection().cursor() as cursor:
        sql = "SELECT * FROM `hubs` WHERE `user_id` = %(id)s"
        cursor.execute(sql, args={'id': int(user_id)})

        devices = []

        for device in cursor:
            devices.append(Hub(device[0], device[1], device[4], device[5], device[2], device[6]))

        return devices

# Define method to get sensors by user
def get_sensors_by_user(user_id: int):
    from entities.devices import Sensor
    
    # Iterate over all hubs, return data in form of dict
    data = {}

    with get_connection().cursor() as cursor:
        sql = "SELECT `sensors`.`id`, `sensors`.`thing_id`, `sensors`.`hub_id`, `sensors`.`zone` FROM `sensors` INNER JOIN `hubs` ON `sensors`.`hub_id` = `hubs`.`id` WHERE `hubs`.`user_id` = %(ui)s"
        cursor.execute(sql, args={'ui': int(user_id)})

        for sensor in cursor:
            if data.get(sensor[2]) == None:
                data[sensor[2]] = [Sensor(sensor[0], sensor[1], sensor[3])]
            else:
                data[sensor[2]].append(Sensor(sensor[0], sensor[1], sensor[3]))

    parsed_data = {}

    for hub in data:
        zone1_sensors = [sensor for sensor in data[hub] if sensor.zone == 1]
        zone2_sensors = [sensor for sensor in data[hub] if sensor.zone == 2]

        parsed_data[hub] = {1: zone1_sensors, 2: zone2_sensors}

    return parsed_data

# # Define method to get devices by user_id from database
# def get_devices_by_user(user_id: str): 
#     from entities.devices import Hub, Sensor
#     with get_connection().cursor() as cursor:
#         sql = "SELECT * FROM `devices` WHERE `user_id` = %(id)s"
#         cursor.execute(sql, args={'id': int(user_id)})

#         devices = {'sensor': [], 'hub': []}

#         for device in cursor:
#             if device[2] == 0:      # Sensor
#                 devices['sensor'].append(Sensor(device[0], device[5], device[3], device[4]))
#             # else:                   # Hub
#                 # devices['hub'].append(Hub(device[0], device[5], device[3], device[4]))

#         return devices

def update_device_threshold(device_id: int, threshold: int, zone: int):
    with get_connection() as cnx:
        with cnx.cursor() as cursor:
            sql = f"UPDATE `hubs` SET `threshold{zone}` = {threshold} WHERE `id` = {device_id}"
            cursor.execute(sql)

        cnx.commit()

def create_reading(device_id: str, reading: str):
    with get_connection() as cnx:
        with cnx.cursor() as cursor:
            sql = "INSERT `readings` (device_id, reading) VALUES (%(di)s, %(m)s)"
            cursor.execute(sql, args={'di': device_id, 'm': reading})

        cnx.commit()
        
def get_readings_for_device(device_id: int, start_date: str, end_date: str) -> list:
    with get_connection().cursor() as cursor:
        sql = 'SELECT * FROM `readings` WHERE `device_id` = %(di)s AND `last_time_updated` BETWEEN %(sd)s AND %(ed)s'
        cursor.execute(sql, args={'di': device_id, 'sd': start_date, 'ed': end_date})

        return [Reading(reading[0], reading[1], reading[2], reading[3]) for reading in cursor]
    
def delete_device_by_id(device_id:int):
    with get_connection() as cnx:
        with cnx.cursor() as cursor:
            sql = 'DELETE FROM `devices` WHERE `id` = %(di)s'
            cursor.execute(sql, args={'di': device_id})
            
        cnx.commit()