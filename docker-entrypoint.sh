#!/bin/bash
set -e

# Function to check if database is ready
wait_for_db() {
  echo "Waiting for database to be ready..."
   host="${DB_HOST}"
   port="${DB_PORT}"

  # Wait for database connection
  while ! nc -z $host $port; do
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

  # Run init-data.sql to populate tables - use the correct path
  echo "Running init-data.sql to populate the database..."
  mysql -h"$DB_HOST" -u"$DB_USER" -p"$DB_PASSWORD" "$DB_DATABASE" < /app/init-data.sql
  echo "Data imported successfully!"
else
  echo "Tables exist. Checking if they have data..."

  # Try to find a table to check
  TABLES=$(mysql -h"$DB_HOST" -u"$DB_USER" -p"$DB_PASSWORD" -e "SHOW TABLES IN $DB_DATABASE;" | tail -n +2)
  SAMPLE_TABLE=$(echo "$TABLES" | head -1)

  if [ -n "$SAMPLE_TABLE" ]; then
    ROW_COUNT=$(mysql -h"$DB_HOST" -u"$DB_USER" -p"$DB_PASSWORD" -e "SELECT COUNT(*) FROM $DB_DATABASE.$SAMPLE_TABLE;" | tail -1)

    if [ "$ROW_COUNT" -eq "0" ]; then
      echo "Table $SAMPLE_TABLE exists but is empty. Populating data..."
      mysql -h"$DB_HOST" -u"$DB_USER" -p"$DB_PASSWORD" "$DB_DATABASE" < /app/init-data.sql
      echo "Data imported successfully!"
    else
      echo "Tables exist and contain data. Skipping initialization."
    fi
  else
    echo "No tables found even though table count is not zero. This is unexpected."
  fi
fi

# Execute the command provided as arguments
exec "$@"
