from setuptools import setup
from gitversion import get_git_version
import os

setup(
    name='django-closuretree',
    version=get_git_version(),
    packages=['closuretree'],
    author='Mike Bryant',
    author_email='mike.bryant@ocado.com',
)
