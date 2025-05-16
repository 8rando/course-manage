#!/bin/bash
set -e

# Function to check if database is ready
wait_for_db() {
  echo "Waiting for database to be ready..."
  host="${DB_HOST:-db}"  # Default to 'db' if variable not set
  port="${DB_PORT:-3306}"  # Default to '3306' if variable not set

  # Debug
  echo "Attempting to connect to database at ${host}:${port}"

  # Wait for database connection - improved command
  until nc -z "$host" "$port" 2>/dev/null; do
    echo "Database is unavailable - sleeping"
    sleep 2
  done

  # Give MariaDB a few extra seconds to initialize
  sleep 5
  echo "Database is up and ready!"
}

# Wait for database to be ready
wait_for_db

# Debug - list files to confirm their location
echo "Checking for SQL files:"
ls -la /app/
ls -la /app/backend/

# First, ensure the database exists
mysql -h"$DB_HOST" -u"$DB_USER" -p"$DB_PASSWORD" -e "CREATE DATABASE IF NOT EXISTS $DB_DATABASE;"

# Check if tables exist
echo "Checking if tables exist..."
TABLE_COUNT=$(mysql -h"$DB_HOST" -u"$DB_USER" -p"$DB_PASSWORD" -e "SELECT COUNT(TABLE_NAME) FROM information_schema.tables WHERE table_schema='$DB_DATABASE';" | tail -1)
if [ "$TABLE_COUNT" -eq "0" ]; then
  echo "No tables found. Running schema.sql..."
  # Run schema.sql to create tables
  mysql -h"$DB_HOST" -u"$DB_USER" -p"$DB_PASSWORD" < /app/backend/schema.sql
  echo "Schema imported successfully!"

  # Execute Python script to populate data directly
  echo "Running generatedata.py to populate the database..."
  # Export database connection details as environment variables for the Python script
#  export DB_HOST="$DB_HOST"
#  export DB_USER="$DB_USER"
#  export DB_PASSWORD="$DB_PASSWORD"
#  export DB_NAME="$DB_DATABASE"

  python /app/backend/generatedata.py || { echo "Failed to populate database"; exit 1; }
  	echo "Data generation completed successfully!"
else
  echo "Tables exist. Checking if they have data..."
  # Try to find a table to check
  TABLES=$(mysql -h"$DB_HOST" -u"$DB_USER" -p"$DB_PASSWORD" -e "SHOW TABLES IN $DB_DATABASE;" | tail -n +2)
  SAMPLE_TABLE=$(echo "$TABLES" | head -1)
  if [ -n "$SAMPLE_TABLE" ]; then
    ROW_COUNT=$(mysql -h"$DB_HOST" -u"$DB_USER" -p"$DB_PASSWORD" -e "SELECT COUNT(*) FROM $DB_DATABASE.$SAMPLE_TABLE;" | tail -1)
    if [ "$ROW_COUNT" -eq "0" ]; then
      echo "Table $SAMPLE_TABLE exists but is empty. Populating data..."

      # Export database connection details as environment variables for the Python script
#      export DB_HOST="$DB_HOST"
#      export DB_USER="$DB_USER"
#      export DB_PASSWORD="$DB_PASSWORD"
#      export DB_NAME="$DB_DATABASE"

      python /app/backend/generatedata.py || { echo "Failed to populate database"; exit 1; }
      echo "Data generation completed successfully!"
    else
      echo "Tables exist and contain data. Skipping initialization."
    fi
  else
    echo "No tables found even though table count is not zero. This is unexpected."
  fi
fi

<< COMMENT
# Ensure nginx configuration is set up correctly
echo "Setting up Nginx configuration..."
if [ -f "/etc/nginx/sites-available/default" ]; then
  echo "Nginx configuration found."

  # Verify nginx is installed
  if command -v nginx &> /dev/null; then
    # Check nginx configuration
    /usr/sbin/nginx -t || { echo "Nginx configuration test failed"; exit 1; }
    echo "Nginx configuration test passed."
  else
    echo "Nginx binary not found in PATH. Checking common locations..."
    if [ -f "/usr/sbin/nginx" ]; then
      echo "Found Nginx at /usr/sbin/nginx"
      /usr/sbin/nginx -t || { echo "Nginx configuration test failed"; exit 1; }
      echo "Nginx configuration test passed."
    else
      echo "ERROR: Nginx not found. Please check installation."
      echo "Continuing without Nginx configuration check..."
    fi
  fi
else
  echo "Nginx configuration missing. Exiting."
  exit 1
fi
COMMENT

# Execute the command provided as arguments
exec "$@"
