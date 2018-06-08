#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='gogtool',
    version=0.1,
    description=('a small extension for lgogdownloader.'
                 'download, automatically install and update local GOG games'),
    license='WTFPL',
    author='dornheimer',
    author_email='iiu@posteo.net',
    packages=find_packages(exclude=['tests']),
    requirements=[
        'setuptools',
        'colorama',
        'PyYAML'
    ],
    entry_points={
        'console_scripts': [
            'gogtool=gogtool.__main__:main',
        ],
    },
)
