# Copyright 2015 Ocado Innovation Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Setup file for django-closuretree."""
from setuptools import setup, find_packages

from closuretree.version import __VERSION__

setup(
    name='django-closuretree',
    version=__VERSION__,
    packages=find_packages(),
    author='Mike Bryant',
    author_email='mike.bryant@ocado.com',
    description='Efficient tree-based datastructure for Django',
    long_description=open('README.rst').read(),
    url='https://github.com/ocadotechnology/django-closuretree/',
    install_requires=[
        'django >= 1.4, < 1.11',
        'django-autoconfig',
    ],
    tests_require=['django-setuptest >= 0.2'],
    test_suite='setuptest.setuptest.SetupTestSuite',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
