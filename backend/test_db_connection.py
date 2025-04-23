import sys
import pymysql
from config import get_db_connection, db_config

def test_connection():
    """
    Tests the database connection and prints connection details.
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        # Try to establish a connection
        connection = get_db_connection()
        
        # Get server information
        server_info = connection.get_server_info()
        
        # Execute a simple query
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 as connection_test")
            result = cursor.fetchone()
            
        # Print connection details
        print("✅ Database connection successful!")
        print(f"   Server: {db_config['host']}:{db_config['port']}")
        print(f"   Database: {db_config['database']}")
        print(f"   User: {db_config['user']}")
        print(f"   Server Version: {server_info}")
        print(f"   Connection Test: {result}")
        
        connection.close()
        return True
        
    except pymysql.MySQLError as e:
        print("❌ Database connection failed!")
        print(f"   Error: {e}")
        return False

if __name__ == "__main__":
    # Run the test and exit with appropriate exit code
    success = test_connection()
    sys.exit(0 if success else 1)