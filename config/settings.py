"""
Django settings for django_crawler project.

Generated by 'django-admin startproject' using Django 5.1.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

import os
from dotenv import load_dotenv
from pytz import timezone as tz

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
}

LOG_DIR = os.getenv("LOG_DIR", os.path.join(BASE_DIR, "logs"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
DEFAULT_TIMEZONE = os.getenv("DEFAULT_TIMEZONE", "Asia/Tehran")
TIME_FORMAT = os.getenv("TIME_FORMAT", "%Y-%m-%d_%H-%M-%S")
LOCAL_TZ = tz(os.getenv("DEFAULT_TIMEZONE", "Asia/Tehran"))

# Ensure logs directory exists
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

from utils.logging import logger


# # Build paths inside the project like this: BASE_DIR / 'subdir'.
# BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!


ALLOWED_HOSTS = []


# Application definition


def read_secret(secret_name):
    """Reads secrets from Docker Secrets or falls back to environment variables."""
    secret_path = os.getenv(f"{secret_name}_FILE")

    if secret_path and os.path.exists(secret_path):
        with open(secret_path, "r") as secret_file:
            return secret_file.read().strip()

    return os.getenv(secret_name.upper())


try:
    # SECURITY WARNING: don't run with debug turned on in production!
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"

    SECRET_KEY = read_secret("SECRET_KEY")

    INSTALLED_APPS = [
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        # Rest framework
        "rest_framework",
        "django_filters",
        # Celery
        "celery",
        "django_celery_beat",
        # Custom apps
        "apps.crawler_app",
        "apps.api_app",
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

    ROOT_URLCONF = "config.urls"

    TEMPLATES = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [os.path.join(BASE_DIR, "templates")],
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

    WSGI_APPLICATION = "config.wsgi.application"

    # Database
    # https://docs.djangoproject.com/en/5.1/ref/settings/#databases

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": read_secret("DATABASE_NAME"),
            "USER": read_secret("DATABASE_USER"),
            "PASSWORD": read_secret("DATABASE_PASSWORD"),
            "HOST": read_secret("DATABASE_HOST"),
            "PORT": read_secret("DATABASE_PORT"),
        }
    }

    # Password validation
    # https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
    # https://docs.djangoproject.com/en/5.1/topics/i18n/

    LANGUAGE_CODE = "en-us"

    TIME_ZONE = "UTC"

    USE_I18N = True

    USE_TZ = True

    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/5.1/howto/static-files/

    # STATIC_URL = "static/"
    STATIC_URL = "/static/"
    STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
    STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
    # Default primary key field type
    # https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

    DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

    REST_FRAMEWORK = {
        "DEFAULT_FILTER_BACKENDS": [
            "django_filters.rest_framework.DjangoFilterBackend"
        ],
        "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
        "PAGE_SIZE": 20,
    }

    # Redis URL for Celery
    CELERY_BROKER_URL = read_secret("REDIS_URL")

    # Store task results in Redis (optional)
    CELERY_RESULT_BACKEND = read_secret("REDIS_URL")

    # Import tasks automatically
    CELERY_IMPORTS = ("apps.crawler_app.tasks",)

    CELERY_ACCEPT_CONTENT = ["json"]
    CELERY_TASK_SERIALIZER = "json"

    logger.info("Django settings loaded successfully!")

except Exception as e:
    logger.critical("Failed to load Django settings", exc_info=True)
    raise e
