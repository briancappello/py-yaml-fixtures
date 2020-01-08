import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

DEBUG = True
SECRET_KEY = "super-secret-key"
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_TZ = True

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "py_yaml_fixtures",
    "django_test_app",
]

AUTH_USER_MODEL = "django_test_app.User"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite"),
    }
}
