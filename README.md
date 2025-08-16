Django News Application 📰
🚀 Introduction
This repository hosts a Django web application designed for fetching and displaying news articles. It provides two flexible deployment methods: running directly via a local Python virtual environment or, as recommended, utilizing Docker Compose for a portable and isolated development setup, including database management.

🛠️ Technologies Used:
- Backend Framework: Django 5.x
  
- Front End: HTML, Tailwind CSS and Javascript
  
- Database: MariaDB / MySQL (with Docker Compose), or configurable for local settings.py.
  
- Containerization: Docker, Docker Compose
  
- Version Control: Git
  
- Python Package Management: pip

⚙️ Setup Instructions:
Follow these steps to get the News Application up and running on your local machine:

Prerequisites
To run this application, ensure you have the following installed on your system:

Python 3.11 or higher

Docker

Docker Compose (typically included with Docker Desktop)

Git

Method 1: Running with a Python Virtual Environment (Local venv)
This method runs the application directly on your local machine using a Python virtual environment.

Clone the repository:

git clone https://github.com/unexpectedlyf/News-App.git
cd News-App

Create and activate a virtual environment:

python3 -m venv venv
source venv/bin/activate # On macOS/Linux
# venv\Scripts\activate   # On Windows (use PowerShell or Git Bash for 'source')

Install project dependencies:

pip install -r requirements.txt

Configure the database:
You will need a running MariaDB or MySQL database instance. Update the DATABASES section in news_project/settings.py with your local database credentials.

# news_project/settings.py (excerpt)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # or 'django.db.backends.mariadb'
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': '127.0.0.1', # or 'localhost'
        'PORT': 3306,
    }
}

Run migrations and start the server:

python manage.py makemigrations
python manage.py migrate
python manage.py runserver

The application will be accessible at http://127.0.0.1:8000.

Method 2: Running with Docker Compose (Recommended)
This method uses Docker to create a portable and isolated environment for your application, including the database, ensuring consistent setup across different environments.

Clone the repository:

git clone https://github.com/unexpectedlyf/News-App.git
cd News-App

Configure Environment Variables:
Open the docker-compose.yml file and replace the placeholder passwords for MARIADB_ROOT_PASSWORD, MARIADB_PASSWORD, and DB_PASSWORD with strong, secure passwords of your choice. It is critical that MARIADB_PASSWORD and DB_PASSWORD are identical.

# docker-compose.yml (excerpt)
services:
  news-db:
    # ...
    environment:
      - MARIADB_ROOT_PASSWORD=your_secure_root_password_here
      - MARIADB_DATABASE=news_db
      - MARIADB_USER=django_user
      - MARIADB_PASSWORD=your_secure_django_password_here # <-- Make this match DB_PASSWORD below
  web:
    # ...
    environment:
      - DB_HOST=news-db
      - DB_NAME=news_db
      - DB_USER=django_user
      - DB_PASSWORD=your_secure_django_password_here # <-- Make this match MARIADB_PASSWORD above

Build and run the application:
From the News-App directory, run the following command. The --build flag will build the Docker image for the web service, and --force-recreate will ensure new containers are created with your updated environment variables.

docker compose up -d --build --force-recreate

Access the application:
Once the containers are running, the application will be available at http://localhost:8000.

📚 Documentation (Sphinx)
This project includes Sphinx documentation located in the docs/ directory. You can build and view the documentation locally after setting up the project.

To build the HTML documentation:

cd docs
make html

Then open _build/html/index.html in your browser.

📞 Contact
For any questions, feedback, or collaborations, please feel free to reach out to [Your Name/unexpectedlyf's email or GitHub profile].

📄 License
This project is open-source and available under the MIT License. See the LICENSE file in the repository for full details.
