import os
from dotenv import load_dotenv
from user import User
import pymysql.cursors

load_dotenv()

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = int(os.getenv('DB_PORT'))

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


# Define method to get user's hashed password from database
def get_user_by_email(email: str):
    with get_connection().cursor() as cursor:
        sql = "SELECT `password` FROM `users` WHERE `email` = %s"
        cursor.execute(sql, (email))
        
        return None if (password := cursor.fetchone()) == None else password[0]

# Define method to get user by id from database
def get_user_by_id(user_id: str):
    with get_connection().cursor() as cursor:
        sql = "SELECT * FROM `users` WHERE `id` = %(id)s"
        cursor.execute(sql, args={'id': int(user_id)})

        return None if (user := cursor.fetchone()) == None else User(user[0], user[1], user[2])