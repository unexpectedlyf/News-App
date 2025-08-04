#!/bin/sh

# This script is used as the entrypoint for the web container.
# Its primary purpose is to wait for the database container to be ready
# before running Django's migrations and starting the development server.

# Echo a message to the console so we know the script has started.
echo "Waiting for the database to be ready..."

# The `nc` (netcat) command is used here to check if the database is
# accepting connections. The host and port are defined in the
# docker-compose.yml file. 'news-db' is the service name, and 3306 is the default
# MariaDB port. The `-z` flag makes `nc` check for an open port
# without sending any data.
while ! nc -z news-db 3306; do
  sleep 0.1 # Wait for a short period before trying again
done

# Echo a message to the console once the database is ready.
echo "Database is ready!"

# Run Django database migrations to apply the schema.
echo "Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# Collect static files.
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Run the Django development server on all available interfaces (0.0.0.0)
# on port 8000.
echo "Starting Django server..."
python manage.py runserver 0.0.0.0:8000
