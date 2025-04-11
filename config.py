import os
from dotenv import load_dotenv
import pymysql

load_dotenv()

# Configuration that works locally and in cloud environments
db_config = {
    'host': os.getenv("DB_HOST", 'localhost'),
    'port': int(os.getenv("DB_PORT", 3306)),
    'user': os.getenv("DB_USER", 'courseadmin'),
    'password': os.getenv("DB_PASSWORD", '1234'),
    'database': os.getenv("DB_DATABASE", 'course_management'),
    'ssl_ca': os.getenv("DB_SSL_CA", None)  # SSL cert for AWS RDS
}

def get_db_connection():
    connect_args = {
        'host': db_config['host'],
        'port': db_config['port'],
        'user': db_config['user'],
        'password': db_config['password'],
        'database': db_config['database'],
        'cursorclass': pymysql.cursors.DictCursor
    }
    
    # Add SSL if configured (needed for AWS RDS)
    if db_config['ssl_ca']:
        connect_args['ssl'] = {'ca': db_config['ssl_ca']}
        
    return pymysql.connect(**connect_args)