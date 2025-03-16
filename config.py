import pymysql

db_config = {
    'host': 'localhost',
    'user': 'courseadmin',
    'password':'1234',
    'database':'course_management'
}

def get_db_connection():
    return pymysql.connect(**db_config)

# Establishes a mysql connection