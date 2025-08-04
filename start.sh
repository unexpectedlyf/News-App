#!/bin/sh
# This script is used as the entrypoint for the web container.
# Its primary purpose is to wait for the database container to be ready
# before running Django's migrations and starting the development server.


# Exit the script if any command fails
set -e

# Wait for MariaDB to be available
echo "Waiting for MariaDB to be available..."
until nc -z -v -w30 news-db 3306
do
  echo "MariaDB is unavailable - sleeping"
  sleep 1
done

echo "MariaDB is up - proceeding with migrations and server startup."

echo "Applying Django database migrations..."
# Run Django database migrations
python manage.py makemigrations
python manage.py migrate

echo "Starting Gunicorn server..."
# Start the Gunicorn web server
# The --bind 0.0.0.0:8000 makes the server listen on all network interfaces
gunicorn --bind 0.0.0.0:8000 news_project.wsgi:application
