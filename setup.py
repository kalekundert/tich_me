#!/usr/bin/env python3
# encoding: utf-8

from setuptools import setup

with open('README.rst') as file:
    readme = file.read()

setup(
    name='tich_me',
    version='0.0.0',
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
)
