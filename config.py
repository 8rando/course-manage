import os
from dotenv import load_dotenv
import pymysql


load_dotenv()

db_config = {
    'host': os.getenv("DB_HOST",'localhost'),
    'port': int(os.getenv("DB_PORT",3306)),
    'user': os.getenv("DB_USER",'courseadmin'),
    'password': os.getenv("DB_PASSWORD",'1234'),
    'database': os.getenv("DB_DATABASE",'course_management')
}

def get_db_connection():
    return pymysql.connect(
        host=db_config['host'],
        port=db_config['port'],
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['database'],
        cursorclass=pymysql.cursors.DictCursor
    )

# Establishes a mysql connection
