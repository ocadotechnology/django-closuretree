# Django settings for testclosure project.

SECRET_KEY = "shh don't tell anyone"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'databasefile',                      # Or path to database file if using sqlite3.
    }
}

INSTALLED_APPS = (
    'closuretree',
    'django_jenkins',
)

try:
    from local_settings import *
except ImportError:
    pass
