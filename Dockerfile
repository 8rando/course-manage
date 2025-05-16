FROM python:3.12-slim

# Install Nginx and MariaDB client for database operations
RUN apt-get update && \
    apt-get install -y \
#    nginx \
    mariadb-client \
    netcat-openbsd \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


# Verify Nginx installation
#RUN which nginx && nginx -v

# Set up working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ /app/backend/
#COPY frontend/ /var/www/html/
#RUN ls -la /var/www/html && chmod -R 755 /var/www/html
COPY docker-entrypoint.sh /app/
#COPY nginx-container.conf /etc/nginx/sites-available/default

# Create symbolic link for Nginx config
#RUN ln -sf /etc/nginx/sites-available/default /etc/nginx/sites-enabled/default

# Make sure directories exist and have proper permissions
RUN mkdir -p /app/backend/
#RUN mkdir -p /var/log/nginx
#RUN chmod -R 755 /var/www/html

# Generate initial data
# RUN python /app/backend/init_data_generator.py > /app/backend/init-data.sql || { echo "Failed to generate init-data.sql"; exit 1; }

# Set permissions for entrypoint script
RUN chmod +x /app/docker-entrypoint.sh

# Expose ports for Nginx (80) and the API (8080)
# 80
EXPOSE 8080

# Define entrypoint and CMD
ENTRYPOINT ["/app/docker-entrypoint.sh"]
#CMD /usr/sbin/nginx -g "daemon off;" & gunicorn --chdir backend --bind 0.0.0.0:8080 app:app
CMD ["gunicorn", "--chdir", "backend", "--bind", "0.0.0.0:8080", "app:app"]
