#!/usr/bin/env python3
# encoding: utf-8

from setuptools import setup

with open('README.rst') as file:
    readme = file.read()

setup(
    name='tich_me',
    version='0.1.3',
    author='Kale Kundert',
    author_email='kale@thekunderts.net',
    long_description=readme,
    packages=[
        'tich_me',
    ],
    entry_points={
        'console_scripts': [
            'tich_me=tich_me.main:main',
        ],
    },
    install_requires=[
        'appdirs',
        'docopt',
        'sqlalchemy',
        'requests',
        'beautifulsoup4',
        'numpy',
        'pandas',
        'matplotlib',
    ],
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Topic :: Games/Entertainment :: Board Games',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
    ],
)
