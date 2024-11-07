from dotenv import load_dotenv

import os
import pymysql.cursors
import random

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

def generate_readings():
    readings = []

    for i in range(12):
        readings.append(('6', f'{random.randint(0, 100)}', f'\'2024-{i+1}-{random.randint(1,9)} 21:48:17\''))
        readings.append(('6', f'{random.randint(0, 100)}', f'\'2024-{i+1}-{random.randint(0,9)+10} 21:48:17\''))
        readings.append(('6', f'{random.randint(0, 100)}', f'\'2024-{i+1}-{random.randint(0,9)+20} 21:48:17\''))

    return readings

# Define method to generate readings_sql
def generate_sql():
    readings = generate_readings()

    sql = str('INSERT INTO `readings` (`device_id`, `reading`, `last_time_updated`) VALUES ')

    for reading in readings:
        sql += f'({', '.join(reading)}), '

    return sql[0:-2] + ';'

# Define method to commit query to DB
def insert_dummy_data():
    sql = generate_sql()
    print(sql)

    with get_connection() as cnx:
        with cnx.cursor() as cursor:
            cursor.execute(sql)
        
        cnx.commit()

if __name__ == '__main__':
    insert_dummy_data()