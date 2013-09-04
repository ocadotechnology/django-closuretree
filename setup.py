from setuptools import setup
import os

from closuretree.version import __VERSION__

setup(
    name='django-closuretree',
    version=__VERSION__,
    packages=['closuretree'],
    author='Mike Bryant',
    author_email='mike.bryant@ocado.com',
    install_requires=['django >= 1.4', 'gitversion >= 2.1.1'],
)
