import os
from dotenv import load_dotenv
import pymysql.cursors

load_dotenv()

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = int(os.getenv('DB_PORT'))

cnx = pymysql.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASS, port=DB_PORT, db=DB_NAME)

with cnx:
    with cnx.cursor() as cursor:
        sql = 'SELECT 2+2'
        cursor.execute(sql)
        result = cursor.fetchone()
        print(result)