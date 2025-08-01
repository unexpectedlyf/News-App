 FROM python:3.11-slim

 # Set working directory
 WORKDIR /app

 # Set environment variables
 ENV PYTHONDONTWRITEBYTECODE 1
 ENV PYTHONUNBUFFERED 1

 # Install system dependencies
 RUN apt-get update && apt-get install -y \
     gcc \
     python3-dev \
     libpq-dev \
     && rm -rf /var/lib/apt/lists/*

 # Install Python dependencies
 COPY requirements.txt .
 RUN pip install --no-cache-dir -r requirements.txt

 # Copy project files
 COPY . .

 # Collect static files (optional, for Django)
 RUN python manage.py collectstatic --noinput

 # Run migrations
 RUN python manage.py migrate

 # Expose port 8000
 EXPOSE 8000

 # Run the application
 CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]