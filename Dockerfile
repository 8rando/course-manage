FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ /app/backend/
#COPY .env /app/

# Generate initialization data during build
RUN python /app/backend/init_data_generator.py > /app/backend/init-data.sql
#RUN python /app/backend/init_data_generator.py
#RUN python /app/backend/init-data.sql

EXPOSE 8080

# Wait for the database to be ready before starting the application
COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh
ENTRYPOINT ["/app/docker-entrypoint.sh"]

CMD ["gunicorn", "--chdir", "backend", "--bind", "0.0.0.0:8080", "app:app"]
