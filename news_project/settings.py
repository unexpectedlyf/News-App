from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-@e^$0j8*!%8v+x!*w7j7&0m-!g+y@s26s1^n21)j#^!t!m7"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "news_app",  # news application
    "rest_framework",  # Django REST Framework
    "rest_framework.authtoken",
    
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "news_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "news_app/templates")
        ],  # Project-level templates directory
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "news_project.wsgi.application"


# Database
# Using SQLite for initial setup, easily switch to MariaDB later.
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
#DATABASES = {
 #   "default": {
  #      "ENGINE": "django.db.backends.sqlite3",
 #       "NAME": BASE_DIR / "db.sqlite3",
  #  }
#}

# Database configuration for MariaDB
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "news_db",
        "USER": "kgutlane",
        "PASSWORD": "Degasio43*1",
        "HOST": "localhost",
        "PORT": "3306",
        "OPTIONS": {
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "static/"
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static")
]  # Optional: for project-wide static files
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")  # Directory for collected static files

# Media files (user uploaded content like article images)
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(
    BASE_DIR, "media"
)  # This will create a 'media' folder in your project root

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Custom User Model
AUTH_USER_MODEL = "news_app.User"  # Points to your custom user model

# Redirect URLs after login/logout
LOGIN_REDIRECT_URL = "/"  # Redirect to home page after successful login
LOGOUT_REDIRECT_URL = "/login/"  # Redirect to login page after logout
LOGIN_URL = "/login/"  # URL for login_required decorator

# Email settings
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "epikailabs@gmail.com"
EMAIL_HOST_PASSWORD = "inlo copg ossi dyvo"
DEFAULT_FROM_EMAIL = "epikailabs@gmail.com"

# Twitter API Credentials
TWITTER_CONSUMER_KEY = "yFtvo4n75QZ4GV6PEg87OkTpC"
TWITTER_CONSUMER_SECRET = "bJnt5vwp3JMNvi2HjFEQURvRcMW37QTKVFB10d5yH7FnuiL2DT"
TWITTER_ACCESS_TOKEN = "1075802747704885251-2csVutIlmZarAzAKsdR59apVclFhds"
TWITTER_ACCESS_TOKEN_SECRET = "53raFf8JJX2VYSZnt4U7baeYDXNDh3QVyjxX0bdAEgS5Z"

# Django REST Framework settings
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",  # For browsable API
        "rest_framework.authentication.BasicAuthentication",  # For Postman
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",  # Default for most GETs
    ],
}
