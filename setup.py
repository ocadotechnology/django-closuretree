from setuptools import setup
from gitversion import get_git_version
import os

setup(
    name='django-closuretree',
    version=get_git_version(__file__),
    packages=['closuretree'],
    author='Mike Bryant',
    author_email='mike.bryant@ocado.com',
    install_requires=['django'],
)
