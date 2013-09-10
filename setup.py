"""Setup file for django-closuretree."""
from setuptools import setup

from closuretree.version import __VERSION__

setup(
    name='django-closuretree',
    version=__VERSION__,
    packages=['closuretree'],
    author='Mike Bryant',
    author_email='mike.bryant@ocado.com',
    install_requires=['django >= 1.4'],
)
