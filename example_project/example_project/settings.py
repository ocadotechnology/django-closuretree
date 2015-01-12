'''Django settings for example_project project.'''
import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': os.path.join(os.path.abspath(os.path.dirname(__file__)),'dbfile'),# Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

TIME_ZONE = 'Europe/London'
LANGUAGE_CODE = 'en-gb'
STATIC_ROOT = os.path.join(os.path.dirname(__file__), 'static')
STATIC_URL = '/static/'
SECRET_KEY = 'j$w9t$1(e7k*=c!ks!z&amp;w0s6af!xrku1%&amp;6!c@_5wwicjg&amp;c_c'

ROOT_URLCONF = 'django_autoconfig.autourlconf'

WSGI_APPLICATION = 'example_project.wsgi.application'

INSTALLED_APPS = (
    'closuretree',
)

try:
    from example_project.local_settings import *
except ImportError:
    pass

from django_autoconfig import autoconfig
autoconfig.configure_settings(globals())
