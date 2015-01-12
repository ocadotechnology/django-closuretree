"""Setup file for django-closuretree."""
from setuptools import setup, find_packages

from closuretree.version import __VERSION__

setup(
    name='django-closuretree',
    version=__VERSION__,
    packages=find_packages(),
    author='Mike Bryant',
    author_email='mike.bryant@ocado.com',
    install_requires=['django >= 1.4'],
    tests_require=['django-setuptest'],
    test_suite='setuptest.setuptest.SetupTestSuite',
)
