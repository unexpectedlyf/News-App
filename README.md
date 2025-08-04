Django News Application
This repository contains a Django web application that fetches news articles. The application can be run using a local Python virtual environment or, as recommended, with Docker Compose.

Prerequisites
To run this application, you will need the following installed on your system:

Python 3.11 or higher

Docker

Docker Compose (comes with Docker Desktop)

Git

Method 1: Running with a Python Virtual Environment (venv)
This method runs the application directly on your local machine using a Python virtual environment.

Clone the repository:

git clone https://github.com/unexpectedlyf/News-App.git
cd News-App

Create and activate a virtual environment:

python3 -m venv venv
source venv/bin/activate

Install project dependencies:

pip install -r requirements.txt

Configure the database:
You will need a running MariaDB or MySQL database. Update the DATABASES section in your_project_name/settings.py with your local database credentials.

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': '127.0.0.1',
        'PORT': 3306,
    }
}

Run migrations and start the server:

python manage.py makemigrations
python manage.py migrate
python manage.py runserver

The application will be accessible at http://127.0.0.1:8000.

Method 2: Running with Docker Compose (Recommended)
This method uses Docker to create a portable and isolated environment for your application, including the database.

Clone the repository:

git clone https://github.com/unexpectedlyf/News-App.git
cd News-App

Configure Environment Variables:
Open the docker-compose.yml file and replace the placeholder passwords for MARIADB_ROOT_PASSWORD, MARIADB_PASSWORD, and DB_PASSWORD with a strong, secure password of your choice. It is critical that MARIADB_PASSWORD and DB_PASSWORD are identical.

# In docker-compose.yml
services:
  news-db:
    # ...
    environment:
      - MARIADB_ROOT_PASSWORD=your_secure_root_password_here
      - MARIADB_DATABASE=news_db
      - MARIADB_USER=django_user
      - MARIADB_PASSWORD=your_secure_django_password_here
    # ...
  web:
    # ...
    environment:
      - DB_HOST=news-db
      - DB_NAME=news_db
      - DB_USER=django_user
      - DB_PASSWORD=your_secure_django_password_here

Build and run the application:
From the News-App directory, run the following command. The --build flag will build the Docker image for the web service, and --force-recreate will ensure new containers are created with your updated environment variables.

docker compose up -d --build --force-recreate

Access the application:
Once the containers are running, the application will be available at http://localhost:8000.

For Reviewer Access (Temporary)
This file should never be committed to a public repository. It is a temporary file to provide a reviewer with access to the necessary credentials.


