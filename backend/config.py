import os
from dotenv import load_dotenv
import pymysql

# Load environment variables
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
    """
    Creates and returns a connection to the database using configuration
    from environment variables with fallback defaults.
    
    Returns:
        pymysql.connections.Connection: A database connection object
    """
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
    
def close_connection(connection):
    """
    Safely closes a database connection
    
    Args:
        connection: The database connection to close
    """
    if connection:
        connection.close()
        
def execute_query(query, params=None, commit=False):
    """
    Executes a database query and returns the results
    
    Args:
        query (str): SQL query to execute
        params (tuple, optional): Parameters for the query
        commit (bool): Whether to commit the transaction
        
    Returns:
        list: Query results as a list of dictionaries
        
    Raises:
        Exception: If there's a database error
    """
    connection = None
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            if commit:
                connection.commit()
                return cursor.lastrowid
            return cursor.fetchall()
    except Exception as e:
        if connection and commit:
            connection.rollback()
        raise e
    finally:
        close_connection(connection)