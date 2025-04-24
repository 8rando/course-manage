FROM python:3.12-slim

# Set up base image and working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install MySQL client for database operations
RUN apt-get update && apt-get install -y mariadb-client netcat-openbsd

# Copy application code
COPY backend/ /app/backend/
COPY docker-entrypoint.sh /app/

# Make sure the directory exists and has proper permissions
RUN mkdir -p /app/backend/

# Run the init data generator with proper error handling
RUN python /app/backend/init_data_generator.py > /app/backend/init-data.sql || { echo "Failed to generate init-data.sql"; exit 1; }

# Debug - check if file was created correctly
RUN ls -la /app/backend/init-data.sql

# Set permissions for entrypoint script
RUN chmod +x /app/docker-entrypoint.sh

# Expose the port for the application
EXPOSE 8080

# Define entrypoint and CMD
ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["gunicorn", "--chdir", "backend", "--bind", "0.0.0.0:8080", "app:app"]
