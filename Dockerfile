FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create a non-root user to run the application
RUN useradd -m appuser
USER appuser

EXPOSE 8080

CMD ["python", "app.py"]