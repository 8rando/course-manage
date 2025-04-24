#!/bin/bash
set -e

# Function to check if database is ready
wait_for_db() {
  echo "Waiting for database to be ready..."
  
  host="${DB_HOST:-db}"
  port="${DB_PORT:-3306}"
  user="${DB_USER:-courseadmin}"
  password="${DB_PASSWORD:-1234}"
  database="${DB_DATABASE:-course_management}"
  
  # Install netcat if needed
  apt-get update && apt-get install -y netcat-openbsd
  
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

# Execute the command provided as arguments
exec "$@"
