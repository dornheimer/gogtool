#!/usr/bin/python3
import os
import sys
from setuptools import setup

setup(
    name='lgog_manager',
    version=0.1,
    license='GPL-3',
    author='iiu',
    author_email='iiu@posteo.net',
    packages=['lgog'],
    scripts=['bin/lgog'],
    data_files=data_files,
    description='Small (and incomplete) extension for lgogdownloader',
)
