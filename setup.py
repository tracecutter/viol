#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

import os
import sys
from distutils import log

if sys.version_info < (2, 6):
    print('ERROR: invx requires at least Python 2.6 to run.')
    sys.exit(1)

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')
with open('VERSION', 'r') as f:
    version = f.readline().rstrip()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='invx',
    version=version,
    url='https://github.com/tracecutter/invx',
    download_url='https://somewhereovertherainbow/invx',
    license="Proprietary License",
    author='John Fogelin',
    author_email='john@bitharmony.com',
    description=('EDF to XSLX Conversion Utility'),
    long_description=readme + '\n\n' + history,
    zip_safe=False,
    keywords='invx',
    classifiers=[
        'Development Status :: 5 - Production',
        'Intended Audience :: Developers',
        'License :: Other/Proprietary License',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utility :: EDF to XSLX',
    ],
    platforms='any',
    packages=find_packages(exclude=['contrib', 'docs', 'test', 'ez_setup']),
    include_package_data=True,
    entry_points={'console_scripts': ['invx=invx:main']},
    install_requires=requirements,
    test_suite='tests',
)
